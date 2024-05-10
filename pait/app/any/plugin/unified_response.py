from pait.plugin.unified_response import UnifiedResponsePlugin as _UnifiedResponsePlugin

from .util import get_plugin

__all__ = ["UnifiedResponsePlugin"]

UnifiedResponsePlugin: "_UnifiedResponsePlugin" = get_plugin("UnifiedResponsePlugin")
