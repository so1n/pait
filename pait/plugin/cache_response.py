import pickle
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple, Type, Union

from redis.asyncio import Redis  # type: ignore
from redis.asyncio import Redis as AsyncioRedis

from pait.app import set_app_attribute
from pait.field import BaseRequestResourceField, ExtraParam
from pait.g import pait_context
from pait.model.response import FileResponseModel
from pait.plugin.base import PostPluginProtocol
from pait.util import FuncSig, get_func_sig

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel
    from pait.plugin.base import PluginManager


class CacheRespExtraParam(ExtraParam):
    pass


class CacheResponsePlugin(PostPluginProtocol):
    _cache_plugin_redis_key: str = "_cache_plugin_redis"
    _cache_name_param_set: Set[str] = set()

    name: str
    lock_name: str
    include_exc: Optional[Tuple[Type[Exception]]] = None
    redis: Union[Redis, AsyncioRedis, None] = None
    enable_cache_name_merge_param: bool
    cache_time: Optional[int]
    timeout: Optional[float]
    sleep: Optional[float]
    blocking_timeout: Optional[float]

    def __post_init__(self, **kwargs: Any) -> None:
        self.lock_name: str = self.name + ":" + "lock"
        self._cache_name_param_set = kwargs.pop("_cache_name_param_set")

    @classmethod
    def check_redis(cls, redis: Union[Redis, AsyncioRedis]) -> None:
        if redis.connection_pool.connection_kwargs["decode_responses"] is False:
            raise ValueError("Please set redis`s param:decode_responses to True")

    @classmethod
    def set_redis_to_app(cls, app: Any, redis: Union[Redis, AsyncioRedis]) -> None:
        cls.check_redis(redis)
        set_app_attribute(app, cls._cache_plugin_redis_key, redis)

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if issubclass(pait_core_model.response_model_list[0], FileResponseModel):
            raise RuntimeError(
                f"Not use {cls.__name__} in {pait_core_model.func.__name__}, "
                f"{cls.__name__} not support {FileResponseModel.__class__.__name__}"
            )
        if kwargs.get("redis", None) is not None:
            cls.check_redis(kwargs["redis"])
        return None

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        name: str = kwargs.get("name", "")
        if not name:
            kwargs["name"] = pait_core_model.func.__qualname__

        cache_name_param_set: Set[str] = set()
        fun_sig: FuncSig = get_func_sig(pait_core_model.func)
        for param in fun_sig.param_list:
            default: Any = param.default
            if not isinstance(default, BaseRequestResourceField):
                continue
            for extra_param in default.extra_param_list:
                if not isinstance(extra_param, CacheRespExtraParam):
                    continue
                cache_name_param_set.add(default.alias or param.name)
        kwargs["_cache_name_param_set"] = cache_name_param_set
        return kwargs

    def _get_redis(self) -> Union[Redis, AsyncioRedis]:
        redis: Union[Redis, AsyncioRedis, None] = self.redis or pait_context.get().app_helper.get_attributes(
            self._cache_plugin_redis_key, None
        )
        if not redis:
            raise ValueError("Not found redis client")
        return redis

    def _loads(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        return pickle.loads(response.encode("latin1"))

    def _dumps(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        return pickle.dumps(response).decode("latin1")

    def _gen_key(self, *args: Any, **kwargs: Any) -> Tuple[str, str]:
        real_key: str = self.name
        real_lock_key: str = self.lock_name
        if self.enable_cache_name_merge_param:
            args_key_list: list = [str(i) for i in args] if args else []
            if kwargs:
                if self._cache_name_param_set:
                    for key in self._cache_name_param_set:
                        args_key_list.append(str(kwargs[key]))
                else:
                    for value in kwargs.values():
                        args_key_list.append(str(value))
            if args_key_list:
                key_join_str = ":".join(args_key_list)
                real_key = f"{self.name}:{key_join_str}"
                real_lock_key = f"{self.lock_name}:{key_join_str}"
        return real_key, real_lock_key

    async def _async_cache(self, context: "PluginContext") -> Any:
        real_key, real_lock_key = self._gen_key(*context.args, **context.kwargs)
        redis: AsyncioRedis = self._get_redis()
        result: Any = await redis.get(real_key)
        if result:
            result = self._loads(result, *context.args, **context.kwargs)
        else:
            async with redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = await redis.get(real_key)
                if result:
                    result = self._loads(result, *context.args, **context.kwargs)
                else:
                    try:
                        result = await super().__call__(context)
                    except Exception as e:
                        if self.include_exc and isinstance(e, self.include_exc):
                            result = e
                        else:
                            raise e
                    await redis.set(  # type: ignore
                        real_key, self._dumps(result, *context.args, **context.kwargs), ex=self.cache_time
                    )
        if isinstance(result, Exception):
            raise result
        return result

    def _cache(self, context: "PluginContext") -> Any:
        real_key, real_lock_key = self._gen_key(*context.args, **context.kwargs)
        redis: Redis = self._get_redis()
        result: Any = redis.get(real_key)
        if result:
            result = self._loads(result, *context.args, **context.kwargs)
        else:
            with redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = redis.get(real_key)
                if result:
                    result = self._loads(result, *context.args, **context.kwargs)
                else:
                    try:
                        result = super().__call__(context)
                    except Exception as e:
                        if self.include_exc and isinstance(e, self.include_exc):
                            result = e
                        else:
                            raise e
                    redis.set(real_key, self._dumps(result, *context.args, **context.kwargs), ex=self.cache_time)
        if isinstance(result, Exception):
            raise result
        return result

    def __call__(self, context: "PluginContext") -> Any:
        if self._is_async_func:
            return self._async_cache(context)
        else:
            return self._cache(context)

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
        """
        :param redis: redis client
        :param include_exc: Exception types that support caching
        :param name: cache key name
        :param enable_cache_name_merge_param:
            Whether to distinguish between different caches by the parameters received by the routing function
        :param cache_time: cache time
        :param timeout: redis lock timeout param
        :param sleep: redis lock sleep param
        :param blocking_timeout: redis lock blocking_timeout param
        """
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
