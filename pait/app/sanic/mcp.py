from typing import Any

from sanic import Sanic, json
from sanic.request import Request
from sanic.response import HTTPResponse

from pait.app.sanic import pait
from pait.mcp import MCP
from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_asgi_tool

__all__ = ["add_mcp_route", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_tool


def encode_content(value: Any) -> str:
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, HTTPResponse):
        body = value.body
        if isinstance(body, bytes):
            return body.decode()
        return str(body)
    return default_encode_content(value)


async def dispatch_http_tool(app: Sanic, *args: Any, **kwargs: Any) -> Any:
    if not app.router.finalized:
        app.router.finalize()
    return await dispatch_asgi_tool(app, *args, **kwargs)


def add_mcp_route(app: Sanic, mcp: MCP, path: str = "/mcp", **kwargs: Any) -> None:

    @pait()
    async def mcp_route(request: Request) -> Any:
        return json(await mcp.handle_message(request.json or {}))

    app.add_route(mcp_route, path, methods=["POST"], **kwargs)
