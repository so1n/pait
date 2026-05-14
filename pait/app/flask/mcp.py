from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

from flask.app import Flask
from flask.wrappers import Response

from pait.mcp.dispatcher import MCPDirectResponse, dispatch_sync_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_wsgi_tool

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

__all__ = ["build_direct_dispatcher", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_sync_tool
dispatch_http_tool = dispatch_wsgi_tool


def encode_content(value: Any) -> str:
    """Encode Flask-specific direct call values for MCP text content."""
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, Response):
        return value.get_data(as_text=True)
    return default_encode_content(value)


def build_direct_dispatcher(app: Flask, direct_dispatcher: Callable) -> Callable:
    """Bind Flask application context around direct MCP tool calls."""

    def _dispatch_direct_tool(core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None) -> Any:
        """Execute a direct call inside ``app.app_context()``."""
        with app.app_context():
            return direct_dispatcher(core_model, arguments)

    return _dispatch_direct_tool
