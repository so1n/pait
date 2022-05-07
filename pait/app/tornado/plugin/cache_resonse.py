from typing import Any, Dict

from tornado.web import RequestHandler

from pait.plugin.cache_response import CacheResponsePlugin as _CacheResponsePlugin

__all__ = ["CacheResponsePlugin"]


class CacheResponsePlugin(_CacheResponsePlugin):
    def _dumps(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        tornado_handle: RequestHandler = args[0]
        cache_dict: Dict[str, Any] = {
            "write_buffer": tornado_handle._write_buffer,
            "status_code": tornado_handle._status_code,
            "headers": tornado_handle._headers,
        }
        return super()._dumps(cache_dict, *args, **kwargs)

    def _loads(self, response: Any, *args: Any, **kwargs: Any) -> Any:
        response = super()._loads(response, *args, **kwargs)
        tornado_handle: RequestHandler = args[0]
        tornado_handle._write_buffer = response["write_buffer"]
        tornado_handle._status_code = response["status_code"]
        tornado_handle._headers = response["headers"]
        return tornado_handle
