from typing import Any

from tornado.web import RequestHandler

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _AsyncCheckJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncCheckJsonRespPlugin"]


class AsyncCheckJsonRespPlugin(JsonProtocol, _AsyncCheckJsonRespPlugin):  # type: ignore
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AsyncCheckJsonRespPlugin, self).__call__(*args, **kwargs)
        self.check_resp_fn(response)
        tornado_handle: RequestHandler = args[0]
        return self.gen_response(tornado_handle, response)
