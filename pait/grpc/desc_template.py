import inspect
from typing import Any

from protobuf_to_pydantic.gen_model import DescTemplate as _DescTemplate

from pait import field as pait_field

__all__ = ["DescTemplate"]


class DescTemplate(_DescTemplate):
    def template_field(self, field: str) -> Any:
        field_class: Any = getattr(pait_field, field, None)
        if not inspect.isclass(field_class) or not issubclass(field_class, pait_field.BaseField):
            raise ValueError(f"{field} is not a valid field")
        return field_class
