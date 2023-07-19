from datetime import date, datetime
from enum import Enum
from json import JSONEncoder
from typing import Any

from _decimal import Decimal
from any_api.openapi.model import LinksModel

from pait._pydanitc_adapter import PydanticUndefinedType
from pait.model.template import TemplateVar


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return int(obj.timestamp())
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, TemplateVar):
            obj = obj.get_value_from_template_context()
            if isinstance(obj, PydanticUndefinedType):
                obj = None
            return obj
        elif isinstance(obj, LinksModel):
            # TODO Now I don't know how to remove the Links Model from Field(pydantic v2)
            return None
        else:
            return super().default(obj)  # pragma: no cover
