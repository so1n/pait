import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Union

from pait import _pydanitc_adapter
from pait.data import PaitCoreProxyModel
from pait.model.core import PaitCoreModel
from pait.openapi.openapi import ParsePaitModel

PaitModelType = Union[PaitCoreModel, PaitCoreProxyModel]

_invalid_name_pattern = re.compile(r"[^a-zA-Z0-9_-]+")


def sanitize_tool_name(name: str) -> str:
    name = _invalid_name_pattern.sub("_", name).strip("_")
    return name or "pait_tool"


def get_mcp_config(pait_model: PaitModelType) -> Mapping[str, Any]:
    extra = getattr(pait_model, "extra", {}) or {}
    if not isinstance(extra, Mapping):
        return {}
    nested_extra = extra.get("extra", {})
    if isinstance(nested_extra, Mapping) and "mcp" in nested_extra:
        mcp_config = nested_extra.get("mcp", {})
    else:
        mcp_config = extra.get("mcp", {})
    return mcp_config if isinstance(mcp_config, Mapping) else {}


def is_mcp_enabled(pait_model: PaitModelType) -> bool:
    return bool(get_mcp_config(pait_model).get("include"))


def _merge_schema(target: Dict[str, Any], source: Dict[str, Any]) -> None:
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
    name: str
    description: str
    input_schema: Dict[str, Any]
    pait_model: PaitModelType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


def build_tool(pait_model: PaitModelType, used_name_set: Optional[set] = None) -> MCPTool:
    mcp_config = get_mcp_config(pait_model)
    name = sanitize_tool_name(str(mcp_config.get("name") or pait_model.operation_id))
    if used_name_set is not None:
        raw_name = name
        index = 2
        while name in used_name_set:
            name = f"{raw_name}_{index}"
            index += 1
        used_name_set.add(name)

    description = str(mcp_config.get("description") or pait_model.desc or pait_model.summary or "")
    return MCPTool(
        name=name,
        description=description,
        input_schema=build_input_schema(pait_model),
        pait_model=pait_model,
    )
