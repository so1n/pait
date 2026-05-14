import json
import sys
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple
from urllib.parse import quote, unquote, unquote_to_bytes, urlencode

from pait.g import config

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


@dataclass
class MCPHTTPRequest(object):
    """Framework-neutral HTTP request built from MCP tool arguments."""

    method: str
    path: str
    query_string: str
    headers: Dict[str, str]
    body: bytes


@dataclass
class MCPHTTPResponse(object):
    """Framework-neutral HTTP response returned by in-process dispatchers."""

    status_code: int
    headers: Dict[str, str]
    body: bytes

    @property
    def is_error(self) -> bool:
        """Return whether the HTTP status code represents an error."""
        return self.status_code >= 400

    def text(self) -> str:
        """Decode response body as text."""
        return self.body.decode()


def _get_mapping(arguments: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    """Return a namespaced MCP argument mapping."""
    value = arguments.get(key, {})
    return value if isinstance(value, Mapping) else {}


def _get_method(core_model: "PaitCoreModel") -> str:
    """Choose the HTTP method used for an in-process tool request."""
    for method in core_model.method_list:
        upper_method = method.upper()
        if upper_method not in {"HEAD", "OPTIONS"}:
            return upper_method
    if core_model.method_list:
        return core_model.method_list[0].upper()
    return "GET"


def _render_path(path: str, path_dict: Mapping[str, Any]) -> str:
    """Render OpenAPI-style path parameters with MCP path arguments."""
    rendered_path = path
    for name, value in path_dict.items():
        rendered_path = rendered_path.replace("{" + name + "}", quote(str(value), safe=""))
    if "{" in rendered_path or "}" in rendered_path:
        raise KeyError("Missing MCP path arguments for url: " + path)
    return rendered_path if rendered_path.startswith("/") else "/" + rendered_path


def _build_body(arguments: Mapping[str, Any], headers: Dict[str, str]) -> bytes:
    """Build an HTTP request body from MCP arguments.

    Form arguments take precedence because they imply
    ``application/x-www-form-urlencoded``. Otherwise body values are passed
    through as bytes/str or JSON-encoded for structured values.
    """
    form_dict = _get_mapping(arguments, "form")
    if form_dict:
        headers.setdefault("content-type", "application/x-www-form-urlencoded")
        return urlencode(form_dict, doseq=True).encode()

    if "body" not in arguments:
        return b""

    body = arguments.get("body")
    if isinstance(body, bytes):
        return body
    if isinstance(body, str):
        return body.encode()

    headers.setdefault("content-type", "application/json")
    return json.dumps(body, cls=config.json_encoder).encode()


def _build_headers(arguments: Mapping[str, Any]) -> Dict[str, str]:
    """Build HTTP headers and a Cookie header from MCP arguments."""
    headers = {str(key).lower(): str(value) for key, value in _get_mapping(arguments, "header").items()}
    cookie_dict = _get_mapping(arguments, "cookie")
    if cookie_dict:
        headers["cookie"] = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
    return headers


def build_http_request(core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None) -> MCPHTTPRequest:
    """Convert an MCP tool call into a framework-neutral HTTP request."""
    arguments = arguments or {}
    headers = _build_headers(arguments)
    body = _build_body(arguments, headers)
    return MCPHTTPRequest(
        method=_get_method(core_model),
        path=_render_path(core_model.openapi_path or core_model.path, _get_mapping(arguments, "path")),
        query_string=urlencode(_get_mapping(arguments, "query"), doseq=True),
        headers=headers,
        body=body,
    )


def _build_wsgi_environ(request: MCPHTTPRequest) -> Dict[str, Any]:
    """Build a minimal WSGI environ for an in-process HTTP request."""
    environ: Dict[str, Any] = {
        "REQUEST_METHOD": request.method,
        "SCRIPT_NAME": "",
        "PATH_INFO": unquote_to_bytes(request.path).decode("latin-1"),
        "QUERY_STRING": request.query_string,
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "REMOTE_ADDR": "127.0.0.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": BytesIO(request.body),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "CONTENT_LENGTH": str(len(request.body)),
    }
    for key, value in request.headers.items():
        header_key = key.replace("-", "_").upper()
        if header_key == "CONTENT_TYPE":
            environ["CONTENT_TYPE"] = value
        elif header_key == "CONTENT_LENGTH":
            environ["CONTENT_LENGTH"] = value
        else:
            environ["HTTP_" + header_key] = value
    return environ


async def dispatch_asgi_tool(
    app: Any, core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None
) -> MCPHTTPResponse:
    """Dispatch an MCP tool call through an ASGI app in-process.

    This creates an ASGI HTTP scope and minimal ``receive``/``send`` callables,
    then collects the response start/body events into ``MCPHTTPResponse``.
    """
    request = build_http_request(core_model, arguments)
    response_status_code = 500
    response_headers: Dict[str, str] = {}
    response_body_list: List[bytes] = []
    receive_count = 0

    async def receive() -> Dict[str, Any]:
        """Send the request body once, then report disconnect."""
        nonlocal receive_count
        receive_count += 1
        if receive_count == 1:
            return {"type": "http.request", "body": request.body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: Mapping[str, Any]) -> None:
        """Collect ASGI response events."""
        nonlocal response_status_code
        if message["type"] == "http.response.start":
            response_status_code = int(message["status"])
            for key, value in message.get("headers", []):
                response_headers[key.decode().lower()] = value.decode()
        elif message["type"] == "http.response.body":
            response_body_list.append(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": request.method,
        "scheme": "http",
        "path": unquote(request.path),
        "raw_path": request.path.encode(),
        "query_string": request.query_string.encode(),
        "headers": [(key.encode(), value.encode()) for key, value in request.headers.items()],
        "client": ("127.0.0.1", 0),
        "server": ("testserver", 80),
        "app": app,
    }
    await app(scope, receive, send)
    return MCPHTTPResponse(response_status_code, response_headers, b"".join(response_body_list))


def dispatch_wsgi_tool(
    app: Any, core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None
) -> MCPHTTPResponse:
    """Dispatch an MCP tool call through a WSGI app in-process."""
    request = build_http_request(core_model, arguments)
    response_status_code = 500
    response_headers: Dict[str, str] = {}
    write_body_list: List[bytes] = []

    def write(data: bytes) -> None:
        """Collect bytes written through the optional WSGI write callable."""
        write_body_list.append(data)

    def start_response(status: str, headers: List[Tuple[str, str]], exc_info: Any = None) -> Any:
        """Capture WSGI status and headers."""
        nonlocal response_status_code
        response_status_code = int(status.split(" ", 1)[0])
        response_headers.update({key.lower(): value for key, value in headers})
        return write

    wsgi_app = getattr(app, "wsgi_app", app)
    response_iter = wsgi_app(_build_wsgi_environ(request), start_response)
    try:
        body = b"".join(write_body_list + list(response_iter))
    finally:
        close = getattr(response_iter, "close", None)
        if close:
            close()
    return MCPHTTPResponse(response_status_code, response_headers, body)
