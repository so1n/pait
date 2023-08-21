from typing import Any

from pait.app.sanic.adapter.response import gen_response
from pait.model.context import ContextModel as PluginContext
from pait.plugin.unified_response import UnifiedResponsePlugin as BaseUnifiedResponsePlugin
from pait.plugin.unified_response import UnifiedResponsePluginProtocol as BaseUnifiedResponsePluginProtocol


def _gen_response(self: BaseUnifiedResponsePluginProtocol, return_value: Any, context: PluginContext) -> Any:
    return gen_response(return_value, self.response_model_class, *context.args, **context.kwargs)


class UnifiedResponsePlugin(BaseUnifiedResponsePlugin):
    _gen_response = _gen_response


class UnifiedResponsePluginProtocol(BaseUnifiedResponsePluginProtocol):
    _gen_response = _gen_response
