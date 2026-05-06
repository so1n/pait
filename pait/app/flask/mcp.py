from typing import Any

from flask import request
from flask.app import Flask
from flask.wrappers import Response

from pait.app.flask import pait
from pait.mcp import MCP
from pait.mcp.dispatcher import MCPDirectResponse, dispatch_sync_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import dispatch_wsgi_tool

__all__ = ["add_mcp_route", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]

dispatch_direct_tool = dispatch_sync_tool
dispatch_http_tool = dispatch_wsgi_tool


def encode_content(value: Any) -> str:
    if isinstance(value, MCPDirectResponse):
        value = value.value
    if isinstance(value, Response):
        return value.get_data(as_text=True)
    return default_encode_content(value)


def add_mcp_route(app: Flask, mcp: MCP, path: str = "/mcp", **kwargs: Any) -> None:
    @pait()
    def mcp_route() -> Any:
        return mcp.handle_message(request.get_json(silent=True) or {})

    app.add_url_rule(path, view_func=mcp_route, methods=["POST"], **kwargs)
