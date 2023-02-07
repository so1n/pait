from importlib import import_module

from pait.app.auto_load_app import auto_load_app_class
from pait.plugin.unified_response import UnifiedResponsePlugin as _UnifiedResponsePlugin

__all__ = ["UnifiedResponsePlugin"]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
UnifiedResponsePlugin: "_UnifiedResponsePlugin" = getattr(
    import_module(pait_app_path + ".plugin"), "UnifiedResponsePlugin"
)
