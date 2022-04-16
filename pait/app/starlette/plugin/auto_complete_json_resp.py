from typing import Any

from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin as _AsyncAutoCompleteJsonRespPlugin
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AutoCompleteJsonRespPlugin", "AsyncAutoCompleteJsonRespPlugin"]


class AsyncAutoCompleteJsonRespPlugin(JsonProtocol, _AsyncAutoCompleteJsonRespPlugin):  # type: ignore
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AsyncAutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        return self.gen_response(response)


class AutoCompleteJsonRespPlugin(JsonProtocol, _AutoCompleteJsonRespPlugin):  # type: ignore
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super(AutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        return self.gen_response(response)
