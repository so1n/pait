from pait.plugin.check_json_resp import CheckJsonRespPlugin as _CheckJsonRespPlugin

from .util import get_plugin

__all__ = ["CheckJsonRespPlugin"]

CheckJsonRespPlugin: "_CheckJsonRespPlugin" = get_plugin("CheckJsonRespPlugin")
