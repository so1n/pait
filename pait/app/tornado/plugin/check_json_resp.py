from typing import Any

from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .unified_response import UnifiedResponsePluginProtocol

__all__ = ["AsyncCheckJsonRespPlugin", "CheckJsonRespPlugin"]


class CheckJsonRespPlugin(UnifiedResponsePluginProtocol, _CheckJsonRespPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(CheckJsonRespPlugin, self).__call__(*args, **kwargs)
        self.check_resp_fn(response)
        return self._gen_response(response, *args, **kwargs)


class AsyncCheckJsonRespPlugin(CheckJsonRespPlugin):
    """"""
