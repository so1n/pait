import asyncio
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
    def __init__(self, arguments: Mapping[str, Any]) -> None:
        self.request = arguments
        self.args: list = []
        self.kwargs: Dict[str, Any] = {}
        self.request_kwargs: Dict[str, Any] = {}
        self._arguments = arguments

    def _get_mapping(self, key: str) -> Mapping[str, Any]:
        value = self._arguments.get(key, {})
        return value if isinstance(value, Mapping) else {}

    def path(self) -> Mapping[str, Any]:
        return self._get_mapping("path")

    def query(self) -> Mapping[str, Any]:
        return self._get_mapping("query")

    def multiquery(self) -> Mapping[str, Any]:
        return self.query()

    def header(self) -> Mapping[str, Any]:
        return self._get_mapping("header")

    def cookie(self) -> Mapping[str, Any]:
        return self._get_mapping("cookie")

    def body(self) -> Any:
        return self._arguments.get("body", {})

    def json(self) -> Any:
        return self.body()

    def form(self) -> Mapping[str, Any]:
        return self._get_mapping("form")

    def multiform(self) -> Mapping[str, Any]:
        return self.form()

    def file(self) -> Mapping[str, Any]:
        return self._get_mapping("file")

    def self(self) -> Dict[str, Any]:
        return self.__dict__


class MCPAppHelper(object):
    def __init__(self, arguments: Mapping[str, Any], cbv_instance: Any = None) -> None:
        self.cbv_instance = cbv_instance
        self.raw_request = arguments
        self.request = MCPRequest(arguments)

    def get_attributes(self, key: str, default: Any = None) -> Any:
        return default


@dataclass
class MCPDirectResponse(object):
    value: Any
    cbv_instance: Any = None


def encode_content(value: Any) -> str:
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


async def dispatch_tool(
    core_model: "PaitCoreModel", arguments: Optional[Mapping[str, Any]] = None, cbv_instance: Any = None
) -> MCPDirectResponse:
    arguments = arguments or {}
    context = ContextModel(
        cbv_instance=cbv_instance,
        app_helper=MCPAppHelper(arguments, cbv_instance=cbv_instance),  # type: ignore[arg-type]
        pait_core_model=core_model,
        args=[],
        kwargs={},
    )
    set_ctx(context)
    result = core_model.main_plugin(context)
    if inspect.isawaitable(result):
        result = await result
    return MCPDirectResponse(result, cbv_instance=cbv_instance)


def run_async(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError("Can not run async MCP handler inside a running event loop")
