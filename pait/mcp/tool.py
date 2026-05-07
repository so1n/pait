import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Literal

from pait import _pydanitc_adapter
from pait.data import PaitCoreProxyModel
from pait.model.core import PaitCoreModel
from pait.openapi.openapi import ParsePaitModel

PaitModelType = Union[PaitCoreModel, PaitCoreProxyModel]
MCPCallMode = Literal["direct", "http"]
MCPConfigCallMode = Literal["", "direct", "http"]

_invalid_name_pattern = re.compile(r"[^a-zA-Z0-9_-]+")


class MCPConfig(BaseModel):
    """Configuration stored in Pait route extra data for MCP export.

    ``call_mode`` is server-side behavior and is not accepted from individual
    ``tools/call`` requests. Leave it empty to use the MCP instance default.
    """

    include: bool = False
    name: str = ""
    description: str = ""
    call_mode: MCPConfigCallMode = Field(
        default="",
        description="Route-level MCP call mode. Empty uses the MCP server default; otherwise use direct or http.",
    )
    read_only: bool = Field(
        default=False,
        description="Expose the tool with MCP annotations.readOnlyHint when the route does not mutate state.",
    )


def sanitize_tool_name(name: str) -> str:
    """Convert an arbitrary route name into an MCP-compatible tool name."""
    name = _invalid_name_pattern.sub("_", name).strip("_")
    return name or "pait_tool"


def _build_mcp_config(value: Any) -> MCPConfig:
    """Normalize dynamic extra data into ``MCPConfig``."""
    if isinstance(value, MCPConfig):
        return value
    if isinstance(value, BaseModel):
        return MCPConfig(**_pydanitc_adapter.model_dump(value))
    if isinstance(value, Mapping):
        return MCPConfig(**value)
    return MCPConfig()


def get_mcp_config(pait_model: PaitModelType) -> MCPConfig:
    """Read MCP configuration from a Pait model.

    Pait decorators can store values either directly under ``extra["mcp"]`` or
    in the nested ``extra["extra"]["mcp"]`` shape produced by some config
    helpers. Both forms are supported here.
    """
    extra = getattr(pait_model, "extra", {}) or {}
    if not isinstance(extra, Mapping):
        return MCPConfig()
    nested_extra = extra.get("extra", {})
    if isinstance(nested_extra, Mapping) and "mcp" in nested_extra:
        mcp_config = nested_extra.get("mcp")
    else:
        mcp_config = extra.get("mcp")
    return _build_mcp_config(mcp_config)


def is_mcp_enabled(pait_model: PaitModelType) -> bool:
    """Return whether a Pait route should be exported as an MCP tool."""
    return get_mcp_config(pait_model).include


def _merge_schema(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """Merge one request model JSON schema into a namespace schema."""
    target.setdefault("type", "object")
    target.setdefault("properties", {})

    for key, value in source.get("properties", {}).items():
        target["properties"][key] = value

    required_list = target.setdefault("required", [])
    for key in source.get("required", []):
        if key not in required_list:
            required_list.append(key)

    for definition_key in ("$defs", "definitions"):
        if source.get(definition_key):
            target.setdefault(definition_key, {}).update(source[definition_key])


def build_input_schema(pait_model: PaitModelType) -> Dict[str, Any]:
    """Build the MCP tool input schema from Pait request models.

    Pait groups route parameters by request source. MCP arguments use the same
    namespaces, for example ``path``, ``query``, ``header`` and ``body``. Each
    namespace gets its own object schema so callers can provide only the sources
    required by the original HTTP route.
    """
    real_model = PaitCoreProxyModel.get_core_model(pait_model)
    parse_model = ParsePaitModel(real_model)
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
    required_namespace_list: List[str] = []

    for param_type, request_model_list in parse_model.http_param_type_dict.items():
        namespace = "query" if param_type == "multiquery" else param_type
        namespace_schema: Dict[str, Any] = schema["properties"].setdefault(
            namespace,
            {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )
        for request_model in request_model_list:
            _merge_schema(namespace_schema, _pydanitc_adapter.model_json_schema(request_model.model))
        if namespace_schema.get("required") and namespace not in required_namespace_list:
            required_namespace_list.append(namespace)

    if required_namespace_list:
        schema["required"] = required_namespace_list
    return schema


@dataclass
class MCPTool(object):
    """MCP tool metadata derived from one Pait route."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    pait_model: PaitModelType
    call_mode: MCPConfigCallMode = ""
    read_only: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Return the MCP ``Tool`` representation."""
        result: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
        if self.read_only:
            result["annotations"] = {"readOnlyHint": True}
        return result


def build_tool(pait_model: PaitModelType, used_name_set: Optional[set] = None) -> MCPTool:
    """Build one MCP tool from a Pait model.

    Tool names are taken from MCP config first, then route metadata. When
    ``used_name_set`` is provided, duplicate names receive a numeric suffix so a
    single MCP server never exposes ambiguous tool names.
    """
    mcp_config = get_mcp_config(pait_model)
    name = sanitize_tool_name(str(mcp_config.name or pait_model.func_name or pait_model.operation_id))
    if used_name_set is not None:
        raw_name = name
        index = 2
        while name in used_name_set:
            name = f"{raw_name}_{index}"
            index += 1
        used_name_set.add(name)

    description = str(mcp_config.description or pait_model.desc or pait_model.summary or "")
    if mcp_config.call_mode and mcp_config.call_mode not in {"direct", "http"}:
        raise ValueError("MCPConfig call_mode must be 'direct', 'http', or empty")
    return MCPTool(
        name=name,
        description=description,
        input_schema=build_input_schema(pait_model),
        pait_model=pait_model,
        call_mode=mcp_config.call_mode,
        read_only=mcp_config.read_only,
    )
