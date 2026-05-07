from typing import Any

from sanic import Sanic
from sanic.response import HTTPResponse

from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_asgi_tool

__all__ = ["dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_tool


def encode_content(value: Any) -> str:
    """Encode Sanic-specific direct call values for MCP text content."""
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, HTTPResponse):
        body = value.body
        if isinstance(body, bytes):
            return body.decode()
        return str(body)
    return default_encode_content(value)


async def dispatch_http_tool(app: Sanic, *args: Any, **kwargs: Any) -> Any:
    """Dispatch a Sanic MCP tool call through the app's ASGI interface."""
    if not app.router.finalized:
        app.router.finalize()
    return await dispatch_asgi_tool(app, *args, **kwargs)
