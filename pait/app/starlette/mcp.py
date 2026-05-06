from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from pait.app.starlette import pait
from pait.mcp import AsyncMCP
from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_asgi_tool

__all__ = ["add_mcp_route", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_tool
dispatch_http_tool = dispatch_asgi_tool


def encode_content(value: Any) -> str:
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, Response) and hasattr(value, "body"):
        body = value.body
        if isinstance(body, bytes):
            return body.decode()
        return str(body)
    return default_encode_content(value)


def add_mcp_route(app: Starlette, mcp: AsyncMCP, path: str = "/mcp", **kwargs: Any) -> None:
    @pait()
    async def mcp_route(request: Request) -> JSONResponse:
        return JSONResponse(await mcp.handle_message(await request.json()))

    app.add_route(path, mcp_route, methods=["POST"], **kwargs)
