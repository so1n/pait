from typing import Any

from pait.app.starlette.adapter.response import gen_unifiled_response
from pait.model.context import ContextModel as PluginContext
from pait.plugin.unified_response import UnifiedResponsePlugin as BaseUnifiedResponse
from pait.plugin.unified_response import UnifiedResponsePluginProtocol as BaseUnifiedResponsePluginProtocol


def _gen_response(self: BaseUnifiedResponsePluginProtocol, return_value: Any, context: PluginContext) -> Any:
    return gen_unifiled_response(return_value, *context.args, response_model_class=self.response_model_class, **context.kwargs)


class UnifiedResponsePluginProtocol(BaseUnifiedResponsePluginProtocol):
    _gen_response = _gen_response


class UnifiedResponsePlugin(BaseUnifiedResponse):
    _gen_response = _gen_response
