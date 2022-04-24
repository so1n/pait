from typing import Any

from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .base import JsonProtocol

__all__ = ["AsyncAutoCompleteJsonRespPlugin", "AutoCompleteJsonRespPlugin"]


class AutoCompleteJsonRespPlugin(JsonProtocol, _AutoCompleteJsonRespPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(AutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        return self.gen_response(response)


class AsyncAutoCompleteJsonRespPlugin(AutoCompleteJsonRespPlugin):
    """"""
