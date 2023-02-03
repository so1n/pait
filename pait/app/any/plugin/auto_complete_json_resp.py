from importlib import import_module

from pait.app.auto_load_app import auto_load_app_class
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

__all__ = ["AutoCompleteJsonRespPlugin"]
pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
AutoCompleteJsonRespPlugin: "_AutoCompleteJsonRespPlugin" = getattr(
    import_module(pait_app_path + ".plugin"), "AutoCompleteJsonRespPlugin"
)
