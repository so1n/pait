from typing import Any

from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class CheckJsonRespPlugin(UnifiedResponsePluginProtocol, _CheckJsonRespPlugin):
    def _sync_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super()._sync_call(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super()._async_call(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)


class AsyncCheckJsonRespPlugin(CheckJsonRespPlugin):
    """"""
