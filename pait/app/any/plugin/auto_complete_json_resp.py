from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

from .util import get_plugin

__all__ = ["AutoCompleteJsonRespPlugin"]
AutoCompleteJsonRespPlugin: "_AutoCompleteJsonRespPlugin" = get_plugin("AutoCompleteJsonRespPlugin")
