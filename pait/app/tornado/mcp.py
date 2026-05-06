import json
from typing import TYPE_CHECKING, Any, List, Mapping, Optional

from tornado.escape import json_encode, utf8
from tornado.httputil import HTTPHeaders
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.mcp import AsyncMCP
from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

__all__ = ["add_mcp_route", "dispatch_direct_tool", "dispatch_http_tool", "encode_content"]


class MCPDirectRequestHandler(RequestHandler):
    def __init__(self) -> None:
        self._status_code = 200
        self._headers = HTTPHeaders()
        self._write_buffer: List[bytes] = []

    def set_status(self, status_code: int, reason: Any = None) -> None:
        self._status_code = status_code

    def set_header(self, name: str, value: Any) -> None:
        self._headers[name] = value

    def write(self, chunk: Any) -> None:
        if isinstance(chunk, dict):
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            chunk = json_encode(chunk)
        self._write_buffer.append(utf8(chunk))


async def dispatch_direct_tool(core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None) -> Any:
    return await dispatch_tool(core_model, arguments, cbv_instance=MCPDirectRequestHandler())


def encode_content(value: Any) -> str:
    if isinstance(value, MCPDirectResponse):
        tornado_handle = value.cbv_instance
        if isinstance(tornado_handle, RequestHandler) and getattr(tornado_handle, "_write_buffer", None):
            return b"".join(tornado_handle._write_buffer).decode()
        value = value.value
    return default_encode_content(value)


async def dispatch_http_tool(app: Application, *args: Any, **kwargs: Any) -> Any:
    raise NotImplementedError("Tornado does not provide an ASGI/WSGI in-process HTTP interface; use direct call mode")


def add_mcp_route(app: Application, mcp: AsyncMCP, path: str = "/mcp", **kwargs: Any) -> None:
    class MCPRequestHandler(RequestHandler):
        @pait()
        async def post(self) -> None:
            payload = json.loads(self.request.body.decode() or "{}")
            self.set_header("Content-Type", "application/json")
            self.write(await mcp.handle_message(payload))

    app.add_handlers(r".*$", [(path, MCPRequestHandler, kwargs)])
