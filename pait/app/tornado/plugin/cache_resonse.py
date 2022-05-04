import pickle
from typing import Any, Callable, Dict

from tornado.web import RequestHandler

from pait.plugin.cache_response import CacheResponsePlugin as _CacheResponsePlugin

__all__ = ["CacheResponsePlugin"]


class CacheResponsePlugin(_CacheResponsePlugin):
    async def _async_cache(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        real_key, real_lock_key = self._gen_key(*args, **kwargs)
        result: Any = await self.redis.get(real_key)
        tornado_handle: RequestHandler = args[0]
        if not result:
            async with self.redis.lock(
                real_lock_key,
                timeout=self.timeout,
                sleep=self.sleep,
                blocking_timeout=self.blocking_timeout,
            ):
                result = await self.redis.get(real_key)
                if not result:
                    await func(*args, **kwargs)
                    cache_dict: Dict[str, Any] = {
                        "write_buffer": tornado_handle._write_buffer,
                        "status_code": tornado_handle._status_code,
                        "headers": tornado_handle._headers,
                    }
                    await self.redis.set(  # type: ignore
                        real_key, pickle.dumps(cache_dict).decode("latin1"), ex=self.cache_time
                    )
                    return None
        cache_dict = pickle.loads(result.encode("latin1"))
        tornado_handle._write_buffer = cache_dict["write_buffer"]
        tornado_handle._status_code = cache_dict["status_code"]
        tornado_handle._headers = cache_dict["headers"]
        return None
