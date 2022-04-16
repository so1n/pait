from typing import Any

from pait.plugin.check_json_resp import AsyncCheckJsonRespPlugin as _AsyncCheckJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncCheckJsonRespPlugin"]


class AsyncCheckJsonRespPlugin(JsonProtocol, _AsyncCheckJsonRespPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AsyncCheckJsonRespPlugin, self).__call__(*args, **kwargs)
        return self.gen_response(response)
