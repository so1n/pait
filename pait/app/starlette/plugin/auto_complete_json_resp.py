from typing import Any

from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AutoCompleteJsonRespPlugin", "AsyncAutoCompleteJsonRespPlugin"]


class AutoCompleteJsonRespPlugin(JsonProtocol, _AutoCompleteJsonRespPlugin):
    def _sync_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super()._sync_call(*args, **kwargs)
        return self.gen_response(response)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super()._async_call(*args, **kwargs)
        return self.gen_response(response)


class AsyncAutoCompleteJsonRespPlugin(AutoCompleteJsonRespPlugin):
    """"""
