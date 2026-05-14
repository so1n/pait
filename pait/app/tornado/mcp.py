from typing import TYPE_CHECKING, Any, List, Mapping, Optional

from tornado.escape import json_encode, utf8
from tornado.httputil import HTTPHeaders
from tornado.web import Application, RequestHandler

from pait.mcp.dispatcher import MCPDirectResponse, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

__all__ = ["dispatch_direct_tool", "dispatch_http_tool", "encode_content"]


class MCPDirectRequestHandler(RequestHandler):
    """Small RequestHandler stub used by Tornado direct calls."""

    def __init__(self) -> None:
        """Initialize the response state used by Tornado response helpers."""
        self._status_code = 200
        self._headers = HTTPHeaders()
        self._write_buffer: List[bytes] = []

    def set_status(self, status_code: int, reason: Any = None) -> None:
        """Store the response status code."""
        self._status_code = status_code

    def set_header(self, name: str, value: Any) -> None:
        """Store a response header."""
        self._headers[name] = value

    def write(self, chunk: Any) -> None:
        """Capture data written by Tornado response helpers."""
        if isinstance(chunk, dict):
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            chunk = json_encode(chunk)
        self._write_buffer.append(utf8(chunk))


async def dispatch_direct_tool(core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None) -> Any:
    """Dispatch a Tornado route directly with a lightweight handler stub."""
    return await dispatch_tool(core_model, arguments, cbv_instance=MCPDirectRequestHandler())


def encode_content(value: Any) -> str:
    """Encode Tornado-specific direct call values for MCP text content."""
    if isinstance(value, MCPDirectResponse):
        tornado_handle = value.cbv_instance
        if isinstance(tornado_handle, RequestHandler) and getattr(tornado_handle, "_write_buffer", None):
            return b"".join(tornado_handle._write_buffer).decode()
        value = value.value
    return default_encode_content(value)


async def dispatch_http_tool(app: Application, *args: Any, **kwargs: Any) -> Any:
    """Reject Tornado HTTP mode because no ASGI/WSGI adapter is available."""
    raise NotImplementedError("Tornado does not provide an ASGI/WSGI in-process HTTP interface; use direct call mode")
