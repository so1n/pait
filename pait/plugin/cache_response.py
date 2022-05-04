import pickle
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Union

from redis import Redis  # type: ignore
from redis.asyncio import Redis as AsyncioRedis  # type: ignore

from pait.plugin.base import PluginProtocol

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel
    from pait.plugin.base import PluginManager


class CacheResponsePlugin(PluginProtocol):
    name: str
    lock_name: str
    redis: Union[Redis, AsyncioRedis]
    enable_cache_name_merge_param: bool
    cache_time: Optional[int]
    timeout: Optional[float]
    sleep: Optional[float]
    blocking_timeout: Optional[float]

    def __post_init__(self, pait_core_model: "PaitCoreModel", args: tuple, kwargs: dict) -> None:
        self.lock_name: str = self.name + ":" + "lock"

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if "pait_response_model" in kwargs:
            raise RuntimeError("Please use response_model_list param")

        if kwargs["redis"].connection_pool.connection_kwargs["decode_responses"] is False:
            raise ValueError("Please set redis`s param:decode_responses to True")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        name: str = kwargs.get("name", "")
        if not name:
            kwargs["name"] = pait_core_model.func.__name__
        kwargs["pait_response_model"] = pait_core_model.response_model_list[0]
        return kwargs

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

    async def _async_cache(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        real_key, real_lock_key = self._gen_key(*args, **kwargs)
        result: Any = await self.redis.get(real_key)
        if not result:
            async with self.redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = await self.redis.get(real_key)
                if not result:
                    result = await func(*args, **kwargs)
                    await self.redis.set(  # type: ignore
                        real_key, pickle.dumps(result).decode("latin1"), ex=self.cache_time
                    )
                    return result
        return pickle.loads(result.encode("latin1"))

    def _cache(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        real_key, real_lock_key = self._gen_key(*args, **kwargs)

        result: Any = self.redis.get(real_key)
        if not result:
            with self.redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = self.redis.get(real_key)
                if not result:
                    result = func(*args, **kwargs)
                    self.redis.set(real_key, pickle.dumps(result).decode("latin1"), ex=self.cache_time)
                    return result
        return pickle.loads(result.encode("latin1"))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._is_async_func:
            return self._async_cache(self.call_next, *args, **kwargs)
        else:
            return self._cache(self.call_next, *args, **kwargs)

    @classmethod
    def build(  # type: ignore
        cls,
        *,
        redis: Union[Redis, AsyncioRedis],
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
            enable_cache_name_merge_param=enable_cache_name_merge_param,
            cache_time=cache_time or 5 * 60,
            timeout=timeout,
            sleep=sleep,
            blocking_timeout=blocking_timeout,
        )
