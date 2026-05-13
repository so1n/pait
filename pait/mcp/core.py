from typing import Any, Dict, Mapping, Optional, Set, Tuple, Union, cast

from pait import __version__
from pait.app.any.util import import_func_from_app
from pait.app.base.simple_route import SimpleRoute
from pait.data import PaitCoreProxyModel
from pait.field import Json
from pait.mcp.dispatcher import dispatch_sync_tool, dispatch_tool
from pait.mcp.dispatcher import encode_content as default_encode_content
from pait.mcp.http import MCPHTTPResponse
from pait.mcp.resource import ResourceRegistry
from pait.mcp.tool import MCPCallMode, MCPConfigCallMode, MCPTool, build_tool, is_mcp_enabled
from pait.mcp.types import (
    AsyncDirectDispatcherType,
    AsyncHTTPDispatcherType,
    ContentEncoderType,
    LoadAppType,
    MCPArgumentsType,
    MCPMessageType,
    MCPResultType,
    MCPRouteType,
    ResourceDecoratorType,
    SyncDirectDispatcherType,
    SyncHTTPDispatcherType,
)

MCP_PROTOCOL_VERSION = "2025-11-25"
MCP_SUPPORTED_PROTOCOL_VERSION_TUPLE = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05", "2024-10-07")


class BaseMCP(object):
    """Shared MCP server state and framework integration.

    BaseMCP owns tool/resource registration, framework route registration, and
    JSON-RPC response formatting. Subclasses only decide whether tool execution
    is synchronous or asynchronous.
    """

    def __init__(
        self,
        app: Any = None,
        load_app: Optional[LoadAppType] = None,
        call_mode: MCPCallMode = "direct",
        http_dispatcher: Optional[Union[AsyncHTTPDispatcherType, SyncHTTPDispatcherType]] = None,
        direct_dispatcher: Optional[Union[AsyncDirectDispatcherType, SyncDirectDispatcherType]] = None,
        content_encoder: Optional[ContentEncoderType] = None,
        mcp_path: Optional[str] = "/mcp",
        server_name: str = "pait",
        server_version: str = __version__,
        **load_app_kwargs: Any,
    ) -> None:
        """Create an MCP facade for a Pait-enabled web application.

        Args:
            app: Optional web framework application. When provided, Pait routes
                are loaded immediately and an MCP endpoint is registered unless
                ``mcp_path`` is None.
            load_app: Optional replacement for the framework's ``load_app``
                function.
            call_mode: ``"direct"`` calls the Pait core model directly;
                ``"http"`` rebuilds an in-process framework request. A route
                can override this default with ``MCPConfig.call_mode``.
            http_dispatcher: Optional function used by HTTP call mode.
            direct_dispatcher: Optional function used by direct call mode.
            content_encoder: Optional function converting tool/resource return
                values into MCP text content.
            mcp_path: MCP endpoint path. Set to None to skip automatic route
                registration and call ``add_mcp_route`` manually later.
            server_name: MCP server implementation name returned by
                ``initialize``.
            server_version: MCP server implementation version returned by
                ``initialize``.
            **load_app_kwargs: Extra keyword arguments forwarded to ``load_app``.
        """
        self._tool_dict: Dict[str, MCPTool] = {}
        self.app = app
        self.call_mode = call_mode
        self.mcp_path = mcp_path
        self.server_name = server_name
        self.server_version = server_version
        self._check_call_mode(call_mode)

        if app is not None and call_mode == "http" and http_dispatcher is None:
            http_dispatcher = import_func_from_app("dispatch_http_tool", app=app, module_name="mcp")
        if app is not None and direct_dispatcher is None:
            direct_dispatcher = self._get_app_direct_dispatcher(app)
        if app is not None and content_encoder is None:
            content_encoder = import_func_from_app("encode_content", app=app, module_name="mcp")

        self.http_dispatcher = http_dispatcher
        self.direct_dispatcher = direct_dispatcher or self._get_default_direct_dispatcher()
        self.content_encoder = content_encoder or default_encode_content
        self._resource_registry = ResourceRegistry(content_encoder=self.content_encoder)

        if app is not None:
            self._load_app(app, load_app=load_app, load_app_kwargs=load_app_kwargs)
            if self.http_dispatcher is None and self._has_http_tool():
                self.http_dispatcher = import_func_from_app("dispatch_http_tool", app=app, module_name="mcp")
            if mcp_path is not None:
                self.add_mcp_route(app, mcp_path)

    @staticmethod
    def _get_default_direct_dispatcher() -> Union[AsyncDirectDispatcherType, SyncDirectDispatcherType]:
        """Return the fallback async direct dispatcher."""
        return dispatch_tool

    def _get_app_direct_dispatcher(self, app: Any) -> Union[AsyncDirectDispatcherType, SyncDirectDispatcherType]:
        """Load the framework direct dispatcher and let the framework wrap it.

        Frameworks can expose ``build_direct_dispatcher(app, dispatcher)`` from
        their ``mcp`` module to bind framework-specific context. Flask uses this
        extension point to enter ``app.app_context()`` without putting Flask
        behavior into the shared MCP core.
        """
        direct_dispatcher = cast(
            Union[AsyncDirectDispatcherType, SyncDirectDispatcherType],
            import_func_from_app("dispatch_direct_tool", app=app, module_name="mcp"),
        )
        try:
            build_direct_dispatcher = import_func_from_app("build_direct_dispatcher", app=app, module_name="mcp")
        except AttributeError:
            return direct_dispatcher
        return cast(
            Union[AsyncDirectDispatcherType, SyncDirectDispatcherType],
            build_direct_dispatcher(app, direct_dispatcher),
        )

    def add_mcp_route(self, app: Any, path: str = "/mcp") -> None:
        """Register the MCP JSON-RPC endpoint on a web framework app.

        The route is installed through ``add_multi_simple_route`` so MCP follows
        the same framework-neutral registration path used by the OpenAPI doc
        routes.
        """
        add_multi_simple_route = import_func_from_app("add_multi_simple_route", app=app)
        add_multi_simple_route(
            app,
            SimpleRoute(url=path, route=self._get_mcp_route(app), methods=["POST"]),
            title="pait_mcp",
        )

    def _get_mcp_route(self, app: Any) -> MCPRouteType:
        """Return the Pait-decorated route used by ``add_mcp_route``."""
        raise NotImplementedError

    def _load_app(
        self, app: Any, load_app: Optional[LoadAppType] = None, load_app_kwargs: Optional[Mapping] = None
    ) -> None:
        """Load Pait routes from the app and convert MCP-enabled routes to tools."""
        load_app_func = load_app or cast(LoadAppType, import_func_from_app("load_app", app=app))
        pait_model_dict = load_app_func(app, **(load_app_kwargs or {}))
        used_name_set: Set[str] = set()
        for pait_model in pait_model_dict.values():
            if not is_mcp_enabled(pait_model):
                continue
            tool = build_tool(pait_model, used_name_set)
            self._tool_dict[tool.name] = tool

    @staticmethod
    def _check_call_mode(call_mode: MCPConfigCallMode) -> None:
        """Validate the tool invocation mode."""
        if call_mode not in {"direct", "http"}:
            raise ValueError("MCP call_mode must be 'direct' or 'http'")

    def _has_http_tool(self) -> bool:
        """Return whether any loaded tool overrides its call mode to HTTP."""
        return any(tool.call_mode == "http" for tool in self._tool_dict.values())

    def list_tools(self) -> MCPResultType:
        """Return MCP ``tools/list`` payload."""
        return {"tools": [tool.to_dict() for tool in self._tool_dict.values()]}

    def resource(
        self,
        uri: str,
        *,
        name: str = "",
        description: str = "",
        mime_type: str = "text/plain",
    ) -> ResourceDecoratorType:
        """Register an MCP resource handler.

        This mirrors decorator-style route registration: the decorated function
        is kept as the resource reader and returned unchanged.
        """
        return self._resource_registry.resource(
            uri,
            name=name,
            description=description,
            mime_type=mime_type,
        )

    def list_resources(self) -> MCPResultType:
        """Return MCP ``resources/list`` payload."""
        return self._resource_registry.list_resources()

    def initialize(self, protocol_version: str = MCP_PROTOCOL_VERSION) -> MCPResultType:
        """Return the MCP ``initialize`` result.

        MCP clients usually call ``initialize`` before regular operations. The
        server replies with the protocol version it wants to use, its supported
        capabilities, and implementation metadata.
        """
        real_protocol_version = (
            protocol_version if protocol_version in MCP_SUPPORTED_PROTOCOL_VERSION_TUPLE else MCP_PROTOCOL_VERSION
        )
        return {
            "protocolVersion": real_protocol_version,
            "capabilities": {
                "resources": {"listChanged": False},
                "tools": {"listChanged": False},
            },
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version,
            },
        }

    @staticmethod
    def ping() -> MCPResultType:
        """Return the MCP ``ping`` result."""
        return {}

    def _get_core_model_and_call_mode(self, tool: MCPTool) -> Tuple[Any, str]:
        """Resolve the concrete Pait core model and configured call mode.

        The mode is intentionally not taken from ``tools/call`` request
        parameters. Tool execution mode is server-side configuration: the MCP
        instance provides the default and ``MCPConfig.call_mode`` can override it
        for one route.
        """
        core_model = PaitCoreProxyModel.get_core_model(tool.pait_model)
        real_call_mode = tool.call_mode or self.call_mode
        self._check_call_mode(real_call_mode)
        return core_model, real_call_mode

    def _build_call_error(self, name: str) -> MCPResultType:
        """Build an MCP tool result for an unknown tool name."""
        return {
            "content": [{"type": "text", "text": f"MCP tool not found: {name}"}],
            "isError": True,
        }

    def _build_call_response(self, value: Any) -> MCPResultType:
        """Convert a dispatcher return value into an MCP tool result."""
        return {
            "content": [{"type": "text", "text": self.content_encoder(value)}],
            "isError": value.is_error if isinstance(value, MCPHTTPResponse) else False,
        }

    def _build_exception_response(self, exc: Exception) -> MCPResultType:
        """Convert a Python exception into an MCP error tool result."""
        return {
            "content": [{"type": "text", "text": str(exc)}],
            "isError": True,
        }

    def _wrap_message_result(self, message: MCPMessageType, result: MCPResultType) -> MCPResultType:
        """Wrap method results as JSON-RPC responses when the request has an id."""
        if "id" in message:
            return {
                "jsonrpc": message.get("jsonrpc", "2.0"),
                "id": message["id"],
                "result": result,
            }
        return result

    def _wrap_message_error(self, message: MCPMessageType, exc: Exception) -> MCPResultType:
        """Wrap exceptions as JSON-RPC errors when the request has an id."""
        error = {"code": -32000, "message": str(exc)}
        if "id" in message:
            return {
                "jsonrpc": message.get("jsonrpc", "2.0"),
                "id": message["id"],
                "error": error,
            }
        return {"error": error}

    def _get_message_method_and_params(self, message: MCPMessageType) -> Tuple[Any, MCPArgumentsType]:
        """Extract and validate the JSON-RPC method and params mapping."""
        method = message.get("method")
        params = message.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, Mapping):
            raise TypeError("MCP params must be a mapping")
        return method, params


class AsyncMCP(BaseMCP):
    """Asynchronous MCP server implementation."""

    def _get_mcp_route(self, app: Any) -> MCPRouteType:
        """Create an async Pait route that handles MCP JSON-RPC messages."""
        pait = import_func_from_app("pait", app=app)

        @pait()
        async def mcp_route(message: Dict[str, Any] = Json.i(default_factory=dict, raw_return=True)) -> MCPResultType:
            return await self.handle_message(message)

        return mcp_route

    async def _call_tool_value(self, tool: MCPTool, arguments: Optional[MCPArgumentsType]) -> Any:
        """Execute a tool and return the raw dispatcher result."""
        core_model, real_call_mode = self._get_core_model_and_call_mode(tool)
        if real_call_mode == "http":
            if not self.app or not self.http_dispatcher:
                raise RuntimeError("MCP http call mode requires app and http_dispatcher")
            return await cast(AsyncHTTPDispatcherType, self.http_dispatcher)(self.app, core_model, arguments)
        return await cast(AsyncDirectDispatcherType, self.direct_dispatcher)(core_model, arguments)

    async def call_tool(self, name: str, arguments: Optional[MCPArgumentsType] = None) -> MCPResultType:
        """Execute an MCP tool by name and return an MCP tool result."""
        tool = self._tool_dict.get(name)
        if not tool:
            return self._build_call_error(name)
        try:
            value = await self._call_tool_value(tool, arguments)
            return self._build_call_response(value)
        except Exception as exc:
            return self._build_exception_response(exc)

    async def read_resource(self, uri: str) -> MCPResultType:
        """Read a registered MCP resource."""
        return await self._resource_registry.read_resource(uri)

    async def handle_message(self, message: MCPMessageType) -> MCPResultType:
        """Handle one JSON-RPC-style MCP message."""
        try:
            result = await self._handle_result(message)
            return self._wrap_message_result(message, result)
        except Exception as exc:
            return self._wrap_message_error(message, exc)

    async def _handle_result(self, message: MCPMessageType) -> MCPResultType:
        """Dispatch supported MCP methods to the matching async handler."""
        method, params = self._get_message_method_and_params(message)
        if method == "initialize":
            return self.initialize(str(params.get("protocolVersion") or MCP_PROTOCOL_VERSION))
        if method in {"notifications/initialized", "ping"}:
            return self.ping()
        if method == "tools/list":
            return self.list_tools()
        if method == "tools/call":
            return await self.call_tool(
                str(params.get("name", "")),
                params.get("arguments") or {},
            )
        if method == "resources/list":
            return self.list_resources()
        if method == "resources/read":
            return await self.read_resource(str(params.get("uri", "")))
        raise KeyError(f"Unsupported MCP method: {method}")


class MCP(BaseMCP):
    """Synchronous MCP server implementation."""

    @staticmethod
    def _get_default_direct_dispatcher() -> SyncDirectDispatcherType:
        """Return the fallback sync direct dispatcher."""
        return dispatch_sync_tool

    def _get_mcp_route(self, app: Any) -> MCPRouteType:
        """Create a sync Pait route that handles MCP JSON-RPC messages."""
        pait = import_func_from_app("pait", app=app)

        @pait()
        def mcp_route(message: Dict[str, Any] = Json.i(default_factory=dict, raw_return=True)) -> MCPResultType:
            return self.handle_message(message)

        return mcp_route

    def _call_tool_value(self, tool: MCPTool, arguments: Optional[MCPArgumentsType]) -> Any:
        """Execute a tool and return the raw dispatcher result."""
        core_model, real_call_mode = self._get_core_model_and_call_mode(tool)
        if real_call_mode == "http":
            if not self.app or not self.http_dispatcher:
                raise RuntimeError("MCP http call mode requires app and http_dispatcher")
            return cast(SyncHTTPDispatcherType, self.http_dispatcher)(self.app, core_model, arguments)
        return cast(SyncDirectDispatcherType, self.direct_dispatcher)(core_model, arguments)

    def call_tool(self, name: str, arguments: Optional[MCPArgumentsType] = None) -> MCPResultType:
        """Execute an MCP tool by name and return an MCP tool result."""
        tool = self._tool_dict.get(name)
        if not tool:
            return self._build_call_error(name)
        try:
            value = self._call_tool_value(tool, arguments)
            return self._build_call_response(value)
        except Exception as exc:
            return self._build_exception_response(exc)

    def read_resource(self, uri: str) -> MCPResultType:
        """Read a registered MCP resource synchronously."""
        return self._resource_registry.read_resource_sync(uri)

    def handle_message(self, message: MCPMessageType) -> MCPResultType:
        """Handle one JSON-RPC-style MCP message synchronously."""
        try:
            result = self._handle_result(message)
            return self._wrap_message_result(message, result)
        except Exception as exc:
            return self._wrap_message_error(message, exc)

    def _handle_result(self, message: MCPMessageType) -> MCPResultType:
        """Dispatch supported MCP methods to the matching sync handler."""
        method, params = self._get_message_method_and_params(message)
        if method == "initialize":
            return self.initialize(str(params.get("protocolVersion") or MCP_PROTOCOL_VERSION))
        if method in {"notifications/initialized", "ping"}:
            return self.ping()
        if method == "tools/list":
            return self.list_tools()
        if method == "tools/call":
            return self.call_tool(
                str(params.get("name", "")),
                params.get("arguments") or {},
            )
        if method == "resources/list":
            return self.list_resources()
        if method == "resources/read":
            return self.read_resource(str(params.get("uri", "")))
        raise KeyError(f"Unsupported MCP method: {method}")
