from pait.plugin.mock_response import MockPluginProtocol as _MockPluginProtocol

from .util import get_plugin

__all__ = ["MockPlugin"]

MockPlugin: "_MockPluginProtocol" = get_plugin("MockPlugin")
