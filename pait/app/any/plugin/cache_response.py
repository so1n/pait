from importlib import import_module

from pait.app.auto_load_app import auto_load_app_class
from pait.plugin.cache_response import CacheResponsePlugin as _CacheResponsePlugin

__all__ = ["CacheResponsePlugin"]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
CacheResponsePlugin: "_CacheResponsePlugin" = getattr(
    import_module(pait_app_path + ".plugin.cache_response"), "CacheResponsePlugin"
)
