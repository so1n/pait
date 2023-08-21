from typing import Any

from pait.model.context import ContextModel as PluginContext
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["AutoCompleteJsonRespPlugin"]


class AutoCompleteJsonRespPlugin(UnifiedResponsePluginProtocol, _AutoCompleteJsonRespPlugin):
    async def __call__(self, context: PluginContext) -> Any:
        response: Any = await super(AutoCompleteJsonRespPlugin, self).__call__(context)
        return self._gen_response(response, context)
