from typing import Any, Callable, Dict, Mapping, Optional, Set, Tuple

from pait.app.any.util import import_func_from_app
from pait.data import PaitCoreProxyModel
from pait.mcp.dispatcher import dispatch_sync_tool, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import MCPHTTPResponse
from pait.mcp.resource import ResourceRegistry
from pait.mcp.tool import MCPTool, build_tool, is_mcp_enabled


class BaseMCP(object):
    def __init__(
        self,
        app: Any = None,
        load_app: Optional[Callable] = None,
        call_mode: str = "direct",
        http_dispatcher: Optional[Callable] = None,
        direct_dispatcher: Optional[Callable] = None,
        content_encoder: Optional[Callable[[Any], str]] = None,
        **load_app_kwargs: Any,
    ) -> None:
        self._tool_dict: Dict[str, MCPTool] = {}
        self._resource_registry = ResourceRegistry()
        self.app = app
        self.call_mode = call_mode
        self._check_call_mode(call_mode)

        if app is not None and call_mode == "http" and http_dispatcher is None:
            http_dispatcher = import_func_from_app("dispatch_http_tool", app=app, module_name="mcp")
        if app is not None and direct_dispatcher is None:
            direct_dispatcher = import_func_from_app("dispatch_direct_tool", app=app, module_name="mcp")
        if app is not None and content_encoder is None:
            content_encoder = import_func_from_app("encode_content", app=app, module_name="mcp")

        self.http_dispatcher = http_dispatcher
        self.direct_dispatcher = direct_dispatcher or self._get_default_direct_dispatcher()
        self.content_encoder = content_encoder or default_encode_content

        if app is not None:
            self._load_app(app, load_app=load_app, load_app_kwargs=load_app_kwargs)

    @staticmethod
    def _get_default_direct_dispatcher() -> Callable:
        return dispatch_tool

    def _load_app(
        self, app: Any, load_app: Optional[Callable] = None, load_app_kwargs: Optional[Mapping] = None
    ) -> None:
        load_app_func = load_app or import_func_from_app("load_app", app=app)
        pait_model_dict = load_app_func(app, **(load_app_kwargs or {}))
        used_name_set: Set[str] = set()
        for pait_model in pait_model_dict.values():
            if not is_mcp_enabled(pait_model):
                continue
            tool = build_tool(pait_model, used_name_set)
            self._tool_dict[tool.name] = tool

    @staticmethod
    def _check_call_mode(call_mode: str) -> None:
        if call_mode not in {"direct", "http"}:
            raise ValueError("MCP call_mode must be 'direct' or 'http'")

    def list_tools(self) -> Dict[str, Any]:
        return {"tools": [tool.to_dict() for tool in self._tool_dict.values()]}

    def resource(
        self,
        uri: str,
        *,
        name: str = "",
        description: str = "",
        mime_type: str = "text/plain",
    ) -> Callable[[Callable], Callable]:
        return self._resource_registry.resource(
            uri,
            name=name,
            description=description,
            mime_type=mime_type,
        )

    def list_resources(self) -> Dict[str, Any]:
        return self._resource_registry.list_resources()

    def _get_core_model_and_call_mode(self, tool: MCPTool, call_mode: Optional[str]) -> Tuple[Any, str]:
        core_model = PaitCoreProxyModel.get_core_model(tool.pait_model)
        real_call_mode = call_mode or self.call_mode
        self._check_call_mode(real_call_mode)
        return core_model, real_call_mode

    def _build_call_error(self, name: str) -> Dict[str, Any]:
        return {
            "content": [{"type": "text", "text": f"MCP tool not found: {name}"}],
            "isError": True,
        }

    def _build_call_response(self, value: Any) -> Dict[str, Any]:
        return {
            "content": [{"type": "text", "text": self.content_encoder(value)}],
            "isError": value.is_error if isinstance(value, MCPHTTPResponse) else False,
        }

    def _build_exception_response(self, exc: Exception) -> Dict[str, Any]:
        return {
            "content": [{"type": "text", "text": str(exc)}],
            "isError": True,
        }

    def _wrap_message_result(self, message: Mapping[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        if "id" in message:
            return {
                "jsonrpc": message.get("jsonrpc", "2.0"),
                "id": message["id"],
                "result": result,
            }
        return result

    def _wrap_message_error(self, message: Mapping[str, Any], exc: Exception) -> Dict[str, Any]:
        error = {"code": -32000, "message": str(exc)}
        if "id" in message:
            return {
                "jsonrpc": message.get("jsonrpc", "2.0"),
                "id": message["id"],
                "error": error,
            }
        return {"error": error}

    def _get_message_method_and_params(self, message: Mapping[str, Any]) -> Any:
        method = message.get("method")
        params = message.get("params") or {}
        if not isinstance(params, Mapping):
            raise TypeError("MCP params must be a mapping")
        return method, params


class AsyncMCP(BaseMCP):
    async def _call_tool_value(
        self, tool: MCPTool, arguments: Optional[Mapping[str, Any]], call_mode: Optional[str]
    ) -> Any:
        core_model, real_call_mode = self._get_core_model_and_call_mode(tool, call_mode)
        if real_call_mode == "http":
            if not self.app or not self.http_dispatcher:
                raise RuntimeError("MCP http call mode requires app and http_dispatcher")
            return await self.http_dispatcher(self.app, core_model, arguments)

        app_context = getattr(self.app, "app_context", None)
        if app_context:
            with app_context():
                return await self.direct_dispatcher(core_model, arguments)
        return await self.direct_dispatcher(core_model, arguments)

    async def call_tool(
        self, name: str, arguments: Optional[Mapping[str, Any]] = None, call_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        tool = self._tool_dict.get(name)
        if not tool:
            return self._build_call_error(name)
        try:
            value = await self._call_tool_value(tool, arguments, call_mode)
            return self._build_call_response(value)
        except Exception as exc:
            return self._build_exception_response(exc)

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        return await self._resource_registry.read_resource(uri)

    async def handle_message(self, message: Mapping[str, Any]) -> Dict[str, Any]:
        try:
            result = await self._handle_result(message)
            return self._wrap_message_result(message, result)
        except Exception as exc:
            return self._wrap_message_error(message, exc)

    async def _handle_result(self, message: Mapping[str, Any]) -> Dict[str, Any]:
        method, params = self._get_message_method_and_params(message)
        if method == "tools/list":
            return self.list_tools()
        if method == "tools/call":
            return await self.call_tool(
                str(params.get("name", "")),
                params.get("arguments") or {},
                call_mode=params.get("callMode") or params.get("call_mode"),
            )
        if method == "resources/list":
            return self.list_resources()
        if method == "resources/read":
            return await self.read_resource(str(params.get("uri", "")))
        raise KeyError(f"Unsupported MCP method: {method}")


class MCP(BaseMCP):
    def __init__(
        self,
        app: Any = None,
        load_app: Optional[Callable] = None,
        call_mode: str = "direct",
        http_dispatcher: Optional[Callable] = None,
        direct_dispatcher: Optional[Callable] = None,
        content_encoder: Optional[Callable[[Any], str]] = None,
        **load_app_kwargs: Any,
    ) -> None:
        super().__init__(
            app,
            load_app=load_app,
            call_mode=call_mode,
            http_dispatcher=http_dispatcher,
            direct_dispatcher=direct_dispatcher,
            content_encoder=content_encoder,
            **load_app_kwargs,
        )

    @staticmethod
    def _get_default_direct_dispatcher() -> Callable:
        return dispatch_sync_tool

    def _call_tool_value(self, tool: MCPTool, arguments: Optional[Mapping[str, Any]], call_mode: Optional[str]) -> Any:
        core_model, real_call_mode = self._get_core_model_and_call_mode(tool, call_mode)
        if real_call_mode == "http":
            if not self.app or not self.http_dispatcher:
                raise RuntimeError("MCP http call mode requires app and http_dispatcher")
            return self.http_dispatcher(self.app, core_model, arguments)

        app_context = getattr(self.app, "app_context", None)
        if app_context:
            with app_context():
                return self.direct_dispatcher(core_model, arguments)
        return self.direct_dispatcher(core_model, arguments)

    def call_tool(
        self, name: str, arguments: Optional[Mapping[str, Any]] = None, call_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        tool = self._tool_dict.get(name)
        if not tool:
            return self._build_call_error(name)
        try:
            value = self._call_tool_value(tool, arguments, call_mode)
            return self._build_call_response(value)
        except Exception as exc:
            return self._build_exception_response(exc)

    def read_resource(self, uri: str) -> Dict[str, Any]:
        return self._resource_registry.read_resource_sync(uri)

    def handle_message(self, message: Mapping[str, Any]) -> Dict[str, Any]:
        try:
            result = self._handle_result(message)
            return self._wrap_message_result(message, result)
        except Exception as exc:
            return self._wrap_message_error(message, exc)

    def handle_message_sync(self, message: Mapping[str, Any]) -> Dict[str, Any]:
        return self.handle_message(message)

    def _handle_result(self, message: Mapping[str, Any]) -> Dict[str, Any]:
        method, params = self._get_message_method_and_params(message)
        if method == "tools/list":
            return self.list_tools()
        if method == "tools/call":
            return self.call_tool(
                str(params.get("name", "")),
                params.get("arguments") or {},
                call_mode=params.get("callMode") or params.get("call_mode"),
            )
        if method == "resources/list":
            return self.list_resources()
        if method == "resources/read":
            return self.read_resource(str(params.get("uri", "")))
        raise KeyError(f"Unsupported MCP method: {method}")
