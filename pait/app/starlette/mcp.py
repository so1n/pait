from typing import Any

from starlette.responses import Response

from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_asgi_tool

__all__ = ["dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_tool
dispatch_http_tool = dispatch_asgi_tool


def encode_content(value: Any) -> str:
    """Encode Starlette-specific direct call values for MCP text content."""
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, Response) and hasattr(value, "body"):
        body = value.body
        if isinstance(body, bytes):
            return body.decode()
        return str(body)
    return default_encode_content(value)
