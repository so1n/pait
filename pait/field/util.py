import inspect
from typing import TYPE_CHECKING, Any, List, Optional, Type

from pydantic import BaseModel

from pait import _pydanitc_adapter
from pait.util import get_pydantic_annotation

from .base import BaseField

if TYPE_CHECKING:
    from .http import BaseRequestResourceField


def is_pait_field(pait_field: Any) -> bool:
    return isinstance(pait_field, BaseField)


def is_pait_field_class(pait_field: Any) -> bool:
    return issubclass(pait_field, BaseField)


def get_parameter_list_from_pydantic_basemodel(
    pait_model: Type[BaseModel],
    default_field_class: Optional[Type["BaseRequestResourceField"]] = None,
) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list = []
    for key, model_field in _pydanitc_adapter.model_fields(pait_model).items():
        pydantic_field = _pydanitc_adapter.get_field_info(model_field)
        if not is_pait_field(pydantic_field):
            if not default_field_class:
                raise TypeError(  # pragma: no cover
                    f"{pydantic_field.__class__} must instance `pait.field.BaseField` by model {pait_model}"
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
