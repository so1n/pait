from importlib import import_module

from pait.app.auto_load_app import auto_load_app_class
from pait.plugin.mock_response import MockPluginProtocol as _MockPluginProtocol

__all__ = ["MockPlugin"]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
MockPlugin: "_MockPluginProtocol" = getattr(import_module(pait_app_path + ".plugin"), "MockPlugin")
