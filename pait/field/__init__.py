from typing import Any

from pait.field.app_resource import Depends
from pait.field.base import BaseField, ExtraParam
from pait.field.request_resource import (
    BaseRequestResourceField,
    Body,
    Cookie,
    File,
    Form,
    Header,
    Json,
    MultiForm,
    MultiQuery,
    Path,
    Query,
)


def is_pait_field(pait_field: Any) -> bool:
    return isinstance(pait_field, BaseField)


def is_pait_field_class(pait_field: Any) -> bool:
    return issubclass(pait_field, BaseField)
