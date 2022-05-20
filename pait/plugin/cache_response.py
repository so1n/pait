import pickle
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Type, Union

from redis import Redis  # type: ignore
from redis.asyncio import Redis as AsyncioRedis  # type: ignore

from pait.app import set_app_attribute
from pait.g import pait_context
from pait.model.response import PaitFileResponseModel
from pait.plugin.base import PluginProtocol

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel
    from pait.plugin.base import PluginManager


_cache_plugin_redis_key: str = "_cache_plugin_redis"


class CacheResponsePlugin(PluginProtocol):
    is_pre_core: bool = False
    name: str
    lock_name: str
    include_exc: Optional[Tuple[Type[Exception]]] = None
    redis: Union[Redis, AsyncioRedis, None] = None
    enable_cache_name_merge_param: bool
    cache_time: Optional[int]
    timeout: Optional[float]
    sleep: Optional[float]
    blocking_timeout: Optional[float]

    def __post_init__(self, pait_core_model: "PaitCoreModel", args: tuple, kwargs: dict) -> None:
        self.lock_name: str = self.name + ":" + "lock"

    @classmethod
    def check_redis(cls, redis: Union[Redis, AsyncioRedis]) -> None:
        if redis.connection_pool.connection_kwargs["decode_responses"] is False:
            raise ValueError("Please set redis`s param:decode_responses to True")

    @classmethod
    def set_redis_to_app(cls, app: Any, redis: Union[Redis, AsyncioRedis]) -> None:
        cls.check_redis(redis)
        set_app_attribute(app, _cache_plugin_redis_key, redis)

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if issubclass(pait_core_model.response_model_list[0], PaitFileResponseModel):
            raise RuntimeError(
                f"Not use {cls.__name__} in {pait_core_model.func.__name__}, "
                f"{cls.__name__} not support {PaitFileResponseModel.__class__.__name__}"
            )
        if "pait_response_model" in kwargs:
            raise RuntimeError("Please use response_model_list param")  # pragma: no cover

        if kwargs.get("redis", None) is not None:
            cls.check_redis(kwargs["redis"])

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        name: str = kwargs.get("name", "")
        if not name:
            kwargs["name"] = pait_core_model.func.__qualname__
        kwargs["pait_response_model"] = pait_core_model.response_model_list[0]
        return kwargs

    def _get_redis(self) -> Union[Redis, AsyncioRedis]:
        redis: Union[Redis, AsyncioRedis, None] = self.redis or pait_context.get().app_helper.get_attributes(
            _cache_plugin_redis_key, None
        )
        if not redis:
            raise ValueError("Not found redis client")
        return redis

    def _gen_key(self, *args: Any, **kwargs: Any) -> Tuple[str, str]:
        real_key: str = self.name
        real_lock_key: str = self.lock_name
        if self.enable_cache_name_merge_param:
            args_key_list: list = []
            if args:
                args_key_list = [str(i) for i in args]
            if kwargs:
                for value in kwargs.values():
                    args_key_list.append(str(value))
            if args_key_list:
                real_key = f"{self.name}:{':'.join(args_key_list)}"
                real_lock_key = f"{self.lock_name}:{':'.join(args_key_list)}"
        return real_key, real_lock_key

    def _loads(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        return pickle.loads(response.encode("latin1"))

    def _dumps(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        return pickle.dumps(response).decode("latin1")

    async def _async_cache(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        real_key, real_lock_key = self._gen_key(*args, **kwargs)
        redis: AsyncioRedis = self._get_redis()
        result: Any = await redis.get(real_key)
        if result:
            result = self._loads(result, *args, **kwargs)
        else:
            async with redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = await redis.get(real_key)
                if result:
                    result = self._loads(result, *args, **kwargs)
                else:
                    try:
                        result = await func(*args, **kwargs)
                    except Exception as e:
                        if self.include_exc and isinstance(e, self.include_exc):
                            result = e
                        else:
                            raise e
                    await redis.set(real_key, self._dumps(result, *args, **kwargs), ex=self.cache_time)  # type: ignore
        if isinstance(result, Exception):
            raise result
        return result

    def _cache(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        real_key, real_lock_key = self._gen_key(*args, **kwargs)
        redis: Redis = self._get_redis()
        result: Any = redis.get(real_key)
        if result:
            result = self._loads(result, *args, **kwargs)
        else:
            with redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = redis.get(real_key)
                if result:
                    result = self._loads(result, *args, **kwargs)
                else:
                    try:
                        result = func(*args, **kwargs)
                    except Exception as e:
                        if self.include_exc and isinstance(e, self.include_exc):
                            result = e
                        else:
                            raise e
                    redis.set(real_key, self._dumps(result, *args, **kwargs), ex=self.cache_time)
        if isinstance(result, Exception):
            raise result
        return result

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._is_async_func:
            return self._async_cache(self.call_next, *args, **kwargs)
        else:
            return self._cache(self.call_next, *args, **kwargs)

    @classmethod
    def build(  # type: ignore
        cls,
        *,
        redis: Union[Redis, AsyncioRedis, None] = None,
        include_exc: Optional[Tuple[Type[Exception]]] = None,
        name: str = "",
        enable_cache_name_merge_param: bool = False,
        cache_time: Optional[int] = None,
        timeout: Optional[float] = None,
        sleep: Optional[float] = None,
        blocking_timeout: Optional[float] = None,
    ) -> "PluginManager":  # type: ignore
        return super().build(
            name=name,
            redis=redis,
            include_exc=include_exc,
            enable_cache_name_merge_param=enable_cache_name_merge_param,
            cache_time=cache_time or 5 * 60,
            timeout=timeout,
            sleep=sleep,
            blocking_timeout=blocking_timeout,
        )
