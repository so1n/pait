from typing import Any

from pait.app.tornado.adapter.response import gen_unifiled_response
from pait.model.context import ContextModel as PluginContext
from pait.plugin.unified_response import UnifiedResponsePlugin as BaseUnifiedResponsePlugin
from pait.plugin.unified_response import UnifiedResponsePluginProtocol as BaseUnifiedResponsePluginProtocol
from pait.util import to_thread


def _gen_response(self: BaseUnifiedResponsePluginProtocol, return_value: Any, context: PluginContext) -> Any:
    return gen_unifiled_response(context.cbv_instance, return_value, *context.args, response_model_class=self.response_model_class, **context.kwargs)


class UnifiedResponsePlugin(BaseUnifiedResponsePlugin):
    _gen_response = _gen_response

    async def __call__(self, context: PluginContext) -> Any:
        # Compatible with tornado cannot call sync routing function
        if self.is_async_mode:
            return await self._async_call(context)
        else:
            return await to_thread(self._sync_call, context)


class UnifiedResponsePluginProtocol(BaseUnifiedResponsePluginProtocol):
    _gen_response = _gen_response
