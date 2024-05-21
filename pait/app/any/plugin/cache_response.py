from pait.plugin.cache_response import CacheResponsePlugin as _CacheResponsePlugin

from .util import get_plugin

__all__ = ["CacheResponsePlugin"]

CacheResponsePlugin: "_CacheResponsePlugin" = get_plugin("CacheResponsePlugin", module_name="cache_response")
