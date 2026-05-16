import sys
import types
from typing import Any, Callable, Mapping, Optional

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpResponse

from pait.mcp.dispatcher import MCPDirectResponse, dispatch_sync_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import MCPHTTPResponse, dispatch_wsgi_tool

__all__ = ["build_direct_dispatcher", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_sync_tool
_MISSING = object()


def encode_content(value: Any) -> str:
    """Encode Django-specific direct call values for MCP text content."""
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, HttpResponse):
        charset = getattr(value, "charset", "utf-8") or "utf-8"
        return value.content.decode(charset)
    return default_encode_content(value)


def build_direct_dispatcher(app: Any, direct_dispatcher: Callable) -> Callable:
    """Keep the Django direct dispatcher signature aligned with other frameworks."""

    def _dispatch_direct_tool(core_model: Any, arguments: Optional[Mapping[str, Any]] = None) -> Any:
        return direct_dispatcher(core_model, arguments)

    return _dispatch_direct_tool


def _get_wsgi_app(app: Any) -> Any:
    if callable(app) and not isinstance(app, (list, tuple)):
        return app
    if not settings.configured:
        raise RuntimeError("Django settings must be configured before using MCP HTTP call mode")
    urlconf_module_name = f"pait_django_mcp_urlconf_{id(app)}"
    urlconf_module = types.ModuleType(urlconf_module_name)
    setattr(urlconf_module, "urlpatterns", list(app))
    sys.modules[urlconf_module_name] = urlconf_module
    settings.ROOT_URLCONF = urlconf_module_name
    return WSGIHandler()


def dispatch_http_tool(app: Any, core_model: Any, arguments: Optional[Mapping[str, Any]] = None) -> MCPHTTPResponse:
    """Dispatch an MCP tool call through Django's WSGI handler in-process."""
    old_urlconf = getattr(settings, "ROOT_URLCONF", _MISSING) if settings.configured else _MISSING
    try:
        return dispatch_wsgi_tool(_get_wsgi_app(app), core_model, arguments)
    finally:
        if old_urlconf is not _MISSING:
            settings.ROOT_URLCONF = old_urlconf
