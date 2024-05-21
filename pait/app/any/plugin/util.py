from importlib import import_module
from typing import Any

from pait.app.auto_load_app import auto_load_app_class


def get_plugin(plugin_name: str, module_name: str = "") -> Any:
    pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
    _module_name = ".plugin"
    if module_name:
        _module_name += "." + module_name
    return getattr(import_module(pait_app_path + _module_name), plugin_name)
