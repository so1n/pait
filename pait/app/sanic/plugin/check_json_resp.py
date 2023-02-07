from typing import Any

from pait.plugin.base import PluginContext
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["CheckJsonRespPlugin"]


class CheckJsonRespPlugin(UnifiedResponsePluginProtocol, _CheckJsonRespPlugin):
    def _sync_call(self, context: PluginContext) -> Any:
        response: Any = super()._sync_call(context)
        return self._gen_response(response, context)

    async def _async_call(self, context: PluginContext) -> Any:
        response: Any = await super()._async_call(context)
        return self._gen_response(response, context)
