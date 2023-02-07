from typing import Any

from pait.app.starlette.adapter.response import gen_response
from pait.plugin.base import PluginContext
from pait.plugin.unified_response import UnifiedResponsePlugin as BaseUnifiedResponse
from pait.plugin.unified_response import UnifiedResponsePluginProtocol as BaseUnifiedResponsePluginProtocol


def _gen_response(self: BaseUnifiedResponsePluginProtocol, return_value: Any, context: PluginContext) -> Any:
    return gen_response(return_value, self.response_model_class, context)


class UnifiedResponsePluginProtocol(BaseUnifiedResponsePluginProtocol):
    _gen_response = _gen_response


class UnifiedResponsePlugin(BaseUnifiedResponse):
    _gen_response = _gen_response
