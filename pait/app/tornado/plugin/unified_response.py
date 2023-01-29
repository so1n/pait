import asyncio
from contextvars import copy_context
from functools import partial
from typing import Any

from pait.app.tornado.adapter.response import gen_response
from pait.plugin.unified_response import UnifiedResponsePlugin as BaseUnifiedResponsePlugin
from pait.plugin.unified_response import UnifiedResponsePluginProtocol as BaseUnifiedResponsePluginProtocol


def _gen_response(self: BaseUnifiedResponsePluginProtocol, return_value: Any, *args: Any, **kwargs: Any) -> Any:
    return gen_response(return_value, self.response_model_class, *args, **kwargs)


class UnifiedResponsePlugin(BaseUnifiedResponsePlugin):
    _gen_response = _gen_response

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # Compatible with tornado cannot call sync routing function
        if self._is_async_func:
            return await self._async_call(*args, **kwargs)
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None, partial(copy_context().run, partial(self._call, *args, **kwargs))  # Matryoshka
            )


class UnifiedResponsePluginProtocol(BaseUnifiedResponsePluginProtocol):
    _gen_response = _gen_response
