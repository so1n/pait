from typing import Any

from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["AsyncAutoCompleteJsonRespPlugin", "AutoCompleteJsonRespPlugin"]


class AutoCompleteJsonRespPlugin(UnifiedResponsePluginProtocol, _AutoCompleteJsonRespPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)


class AsyncAutoCompleteJsonRespPlugin(AutoCompleteJsonRespPlugin):
    """"""
