from typing import Any

from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class CheckJsonRespPlugin(JsonProtocol, _CheckJsonRespPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(CheckJsonRespPlugin, self).__call__(*args, **kwargs)
        return self.gen_response(response)


class AsyncCheckJsonRespPlugin(CheckJsonRespPlugin):
    """"""
