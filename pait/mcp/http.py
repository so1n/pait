import json
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple
from urllib.parse import quote, urlencode

from pait.g import config

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


@dataclass
class MCPHTTPRequest(object):
    method: str
    path: str
    query_string: str
    headers: Dict[str, str]
    body: bytes


@dataclass
class MCPHTTPResponse(object):
    status_code: int
    headers: Dict[str, str]
    body: bytes

    @property
    def is_error(self) -> bool:
        return self.status_code >= 400

    def text(self) -> str:
        return self.body.decode()


def _get_mapping(arguments: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = arguments.get(key, {})
    return value if isinstance(value, Mapping) else {}


def _get_method(core_model: "PaitCoreModel") -> str:
    for method in core_model.method_list:
        upper_method = method.upper()
        if upper_method not in {"HEAD", "OPTIONS"}:
            return upper_method
    if core_model.method_list:
        return core_model.method_list[0].upper()
    return "GET"


def _render_path(path: str, path_dict: Mapping[str, Any]) -> str:
    rendered_path = path
    for name, value in path_dict.items():
        rendered_path = rendered_path.replace("{" + name + "}", quote(str(value), safe=""))
    if "{" in rendered_path or "}" in rendered_path:
        raise KeyError("Missing MCP path arguments for url: " + path)
    return rendered_path if rendered_path.startswith("/") else "/" + rendered_path


def _build_body(arguments: Mapping[str, Any], headers: Dict[str, str]) -> bytes:
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
    headers = {str(key).lower(): str(value) for key, value in _get_mapping(arguments, "header").items()}
    cookie_dict = _get_mapping(arguments, "cookie")
    if cookie_dict:
        headers["cookie"] = "; ".join([f"{key}={value}" for key, value in cookie_dict.items()])
    return headers


def build_http_request(core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None) -> MCPHTTPRequest:
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


async def dispatch_asgi_tool(
    app: Any, core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None
) -> MCPHTTPResponse:
    request = build_http_request(core_model, arguments)
    response_status_code = 500
    response_headers: Dict[str, str] = {}
    response_body_list: List[bytes] = []
    receive_count = 0

    async def receive() -> Dict[str, Any]:
        nonlocal receive_count
        receive_count += 1
        if receive_count == 1:
            return {"type": "http.request", "body": request.body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: Mapping[str, Any]) -> None:
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
        "path": request.path,
        "raw_path": request.path.encode(),
        "query_string": request.query_string.encode(),
        "headers": [(key.encode(), value.encode()) for key, value in request.headers.items()],
        "client": ("127.0.0.1", 0),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    return MCPHTTPResponse(response_status_code, response_headers, b"".join(response_body_list))


async def dispatch_wsgi_tool(
    app: Any, core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None
) -> MCPHTTPResponse:
    from werkzeug.test import EnvironBuilder

    request = build_http_request(core_model, arguments)
    response_status_code = 500
    response_headers: Dict[str, str] = {}
    write_body_list: List[bytes] = []

    def write(data: bytes) -> None:
        write_body_list.append(data)

    def start_response(status: str, headers: List[Tuple[str, str]], exc_info: Any = None) -> Any:
        nonlocal response_status_code
        response_status_code = int(status.split(" ", 1)[0])
        response_headers.update({key.lower(): value for key, value in headers})
        return write

    builder = EnvironBuilder(
        path=request.path,
        method=request.method,
        query_string=request.query_string,
        headers=list(request.headers.items()),
        input_stream=BytesIO(request.body),
        content_length=len(request.body),
        content_type=request.headers.get("content-type"),
    )
    response_iter = app.wsgi_app(builder.get_environ(), start_response)
    try:
        body = b"".join(write_body_list + list(response_iter))
    finally:
        close = getattr(response_iter, "close", None)
        if close:
            close()
    return MCPHTTPResponse(response_status_code, response_headers, body)
