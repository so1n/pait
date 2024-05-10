from importlib import import_module
from typing import Any

from pait.app.auto_load_app import auto_load_app_class


def get_security(security_name: str, module_name: str) -> Any:
    pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower() + ".security." + module_name
    return getattr(import_module(pait_app_path), security_name)
