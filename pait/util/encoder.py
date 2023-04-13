from datetime import date, datetime
from enum import Enum
from json import JSONEncoder
from typing import Any

from _decimal import Decimal
from pydantic.fields import UndefinedType

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
            if isinstance(obj, UndefinedType):
                obj = None
            return obj
        else:
            return super().default(obj)  # pragma: no cover
