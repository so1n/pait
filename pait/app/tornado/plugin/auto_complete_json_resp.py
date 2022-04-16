from typing import Any

from tornado.web import RequestHandler

from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin as _AsyncAutoCompleteJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncAutoCompleteJsonRespPlugin"]


class AsyncAutoCompleteJsonRespPlugin(JsonProtocol, _AsyncAutoCompleteJsonRespPlugin):  # type: ignore
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AsyncAutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        tornado_handle: RequestHandler = args[0]
        return self.gen_response(tornado_handle, response)
