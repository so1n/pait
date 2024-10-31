from typing import Any

from pait.field.app import Depends
from pait.field.base import BaseField, ExtraParam
from pait.field.http import (
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
from pait.field.util import is_pait_field, is_pait_field_class
