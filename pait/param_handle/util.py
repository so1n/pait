import inspect
from typing import Any, Dict, List, Optional, Type, get_type_hints

from pydantic import BaseModel

from pait import _pydanitc_adapter, field
from pait.field import is_pait_field
from pait.util import get_pydantic_annotation

_class_parameter_list_dict: Dict[type, List["inspect.Parameter"]] = {}


def get_parameter_list_from_pydantic_basemodel(
    pait_model: Type[BaseModel],
    default_field_class: Optional[Type[field.request_resource.BaseRequestResourceField]] = None,
) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list = []
    for key, model_field in _pydanitc_adapter.model_fields(pait_model).items():
        pydantic_field = _pydanitc_adapter.get_field_info(model_field)
        if not field.is_pait_field(pydantic_field):
            if not default_field_class:
                raise TypeError(  # pragma: no cover
                    f"{pydantic_field.__class__} must instance {field.request_resource.BaseRequestResourceField} or"
                    f" {field.Depends} by model {pait_model}"
                )
            pydantic_field = default_field_class.from_pydantic_field(pydantic_field)
            pydantic_field.set_request_key(key)
        parameter = inspect.Parameter(
            key,
            inspect.Parameter.POSITIONAL_ONLY,
            default=pydantic_field,
            annotation=get_pydantic_annotation(key, pait_model),
        )
        parameter_list.append(parameter)
    return parameter_list


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list: Optional[List["inspect.Parameter"]] = _class_parameter_list_dict.get(cbv_class)
    if parameter_list is not None:
        return parameter_list
    parameter_list = []
    if hasattr(cbv_class, "__annotations__"):
        for param_name, param_annotation in get_type_hints(cbv_class).items():
            default: Any = getattr(cbv_class, param_name, _pydanitc_adapter.PydanticUndefined)
            if not is_pait_field(default):
                continue

            # Optimize parsing speed
            default.set_request_key(param_name)
            parameter: "inspect.Parameter" = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default,
                annotation=param_annotation,
            )
            parameter_list.append(parameter)
    _class_parameter_list_dict[cbv_class] = parameter_list
    return parameter_list
