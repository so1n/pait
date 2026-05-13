import inspect
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional

from pydantic import BaseModel

from pait import _pydanitc_adapter
from pait.g import config, set_ctx
from pait.mcp.http import MCPHTTPResponse
from pait.model.context import ContextModel

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class MCPRequest(object):
    """Request adapter used by direct MCP tool calls.

    Direct mode does not enter a real web framework request. This object exposes
    the same resource access methods that Pait field parsers expect, backed by
    the MCP tool argument mapping.
    """

    def __init__(self, arguments: Mapping[str, Any]) -> None:
        """Store the MCP tool arguments used as request data."""
        self._arguments = arguments

    @property
    def request(self) -> Any:
        """Reject framework request access in direct MCP mode."""
        raise RuntimeError(
            "MCP direct call mode cannot provide a framework request object; "
            "use MCPConfig(call_mode='http') or remove the request parameter"
        )

    def _get_mapping(self, key: str) -> Mapping[str, Any]:
        """Return a named argument namespace only when it is mapping-like."""
        value = self._arguments.get(key, {})
        return value if isinstance(value, Mapping) else {}

    def path(self) -> Mapping[str, Any]:
        """Return path arguments."""
        return self._get_mapping("path")

    def query(self) -> Mapping[str, Any]:
        """Return query arguments."""
        return self._get_mapping("query")

    def multiquery(self) -> Mapping[str, Any]:
        """Return repeated query arguments."""
        return self.query()

    def header(self) -> Mapping[str, Any]:
        """Return header arguments."""
        return self._get_mapping("header")

    def cookie(self) -> Mapping[str, Any]:
        """Return cookie arguments."""
        return self._get_mapping("cookie")

    def body(self) -> Any:
        """Return request body arguments."""
        return self._arguments.get("body", {})

    def json(self) -> Any:
        """Return JSON arguments. Direct mode treats JSON as the body."""
        return self.body()

    def form(self) -> Mapping[str, Any]:
        """Return form arguments."""
        return self._get_mapping("form")

    def multiform(self) -> Mapping[str, Any]:
        """Return repeated form arguments."""
        return self.form()

    def file(self) -> Mapping[str, Any]:
        """Return file arguments."""
        return self._get_mapping("file")

    def self(self) -> Dict[str, Any]:
        """Return this adapter state for Pait self-field access."""
        return self.__dict__


class MCPAppHelper(object):
    """Minimal AppHelper implementation for direct MCP execution."""

    def __init__(self, arguments: Mapping[str, Any], cbv_instance: Any = None) -> None:
        """Create a direct-mode app helper from MCP arguments."""
        self.cbv_instance = cbv_instance
        self.raw_request = arguments
        self.request = MCPRequest(arguments)

    def get_attributes(self, key: str, default: Any = None) -> Any:
        """Return framework app attributes.

        Direct mode has no real framework app helper, so unsupported attributes
        fall back to the caller-provided default.
        """
        return default


@dataclass
class MCPDirectResponse(object):
    """Raw result returned by a direct MCP dispatcher."""

    value: Any
    cbv_instance: Any = None


def encode_content(value: Any) -> str:
    """Encode a dispatcher/resource value as MCP text content."""
    if isinstance(value, MCPDirectResponse):
        value = value.value

    if isinstance(value, BaseModel):
        value = _pydanitc_adapter.model_dump(value)
    elif isinstance(value, MCPHTTPResponse):
        return value.text()
    elif isinstance(value, bytes):
        return value.decode()

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, cls=config.json_encoder)
    return str(value)


def _dispatch_tool(
    core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None, cbv_instance: Any = None
) -> Any:
    """Run an async-capable Pait core model without a framework request.

    The dispatcher builds the Pait ``ContextModel`` from MCP arguments, installs
    it as the current context, and then executes the route plugin stack. Awaitable
    results are awaited so both sync and async routes can be used by AsyncMCP.
    """
    arguments = arguments or {}
    context = ContextModel(
        cbv_instance=cbv_instance,
        app_helper=MCPAppHelper(arguments, cbv_instance=cbv_instance),  # type: ignore[arg-type]
        pait_core_model=core_model,
        args=[],
        kwargs={},
    )
    set_ctx(context)
    return core_model.main_plugin(context)


async def dispatch_tool(
    core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None, cbv_instance: Any = None
) -> MCPDirectResponse:
    """Run an async-capable Pait core model without a framework request.

    The dispatcher builds the Pait ``ContextModel`` from MCP arguments, installs
    it as the current context, and then executes the route plugin stack. Awaitable
    results are awaited so both sync and async routes can be used by AsyncMCP.
    """
    result = _dispatch_tool(core_model, arguments, cbv_instance)
    if inspect.isawaitable(result):
        result = await result
    return MCPDirectResponse(result, cbv_instance=cbv_instance)


def dispatch_sync_tool(
    core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None, cbv_instance: Any = None
) -> MCPDirectResponse:
    """Run a synchronous Pait core model without a framework request.

    Unlike ``dispatch_tool``, this function never awaits the route result. It is
    used by the sync ``MCP`` class so async routes fail clearly instead of
    silently crossing event-loop boundaries.
    """
    result = _dispatch_tool(core_model, arguments, cbv_instance)
    return MCPDirectResponse(result, cbv_instance=cbv_instance)
