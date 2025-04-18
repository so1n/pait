from dataclasses import MISSING
from typing import Any, Tuple, Type

from sanic.request import Request as _Request

try:
    from sanic.views import CompositionView, HTTPMethodView

    cbv_type_tuple: Tuple[Type, ...] = (HTTPMethodView, CompositionView)
except ImportError:
    from sanic.views import HTTPMethodView

    cbv_type_tuple = (HTTPMethodView,)

from pait.app.base import BaseAppHelper
from pait.app.sanic.adapter.attribute import get_app_attribute
from pait.app.sanic.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[_Request, RequestExtend]):
    CbvType = cbv_type_tuple
    app_name = "sanic"

    request_class = Request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        return get_app_attribute(self.raw_request.app, key, default)
