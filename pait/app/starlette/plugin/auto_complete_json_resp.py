from typing import Any

from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["AutoCompleteJsonRespPlugin", "AsyncAutoCompleteJsonRespPlugin"]


class AutoCompleteJsonRespPlugin(UnifiedResponsePluginProtocol, _AutoCompleteJsonRespPlugin):
    def _sync_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super()._sync_call(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super()._async_call(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)


class AsyncAutoCompleteJsonRespPlugin(AutoCompleteJsonRespPlugin):
    """"""
