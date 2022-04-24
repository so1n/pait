from typing import Any

from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class CheckJsonRespPlugin(JsonProtocol, _CheckJsonRespPlugin):
    def _sync_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super()._sync_call(*args, **kwargs)
        return self.gen_response(response)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super()._async_call(*args, **kwargs)
        return self.gen_response(response)


class AsyncCheckJsonRespPlugin(CheckJsonRespPlugin):
    """"""
