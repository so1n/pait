from importlib import import_module

from pait.app.auto_load_app import auto_load_app_class
from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

__all__ = ["CheckJsonRespPlugin"]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
CheckJsonRespPlugin: "_CheckJsonRespPlugin" = getattr(import_module(pait_app_path + ".plugin"), "CheckJsonRespPlugin")
