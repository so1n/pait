from typing import Any, Dict, Tuple

from tornado.web import RequestHandler

from pait.plugin.cache_response import CacheRespExtraParam
from pait.plugin.cache_response import CacheResponsePlugin as _CacheResponsePlugin

__all__ = ["CacheResponsePlugin", "CacheRespExtraParam"]


class CacheResponsePlugin(_CacheResponsePlugin):
    def _gen_key(self, *args: Any, **kwargs: Any) -> Tuple[str, str]:
        return super()._gen_key(*args[1:], **kwargs)

    def _dumps(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        tornado_handle: RequestHandler = args[0]
        if isinstance(response, Exception):
            return super()._dumps(response, *args, **kwargs)
        cache_dict: Dict[str, Any] = {
            "write_buffer": tornado_handle._write_buffer,
            "status_code": tornado_handle._status_code,
            "headers": tornado_handle._headers,
        }
        return super()._dumps(cache_dict, *args, **kwargs)

    def _loads(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        response = super()._loads(response, *args, **kwargs)
        if isinstance(response, Exception):
            return response
        tornado_handle: RequestHandler = args[0]
        tornado_handle._write_buffer = response["write_buffer"]
        tornado_handle._status_code = response["status_code"]
        tornado_handle._headers = response["headers"]
        return tornado_handle
