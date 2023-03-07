from dataclasses import MISSING
from typing import Any, List

from flask import Request as _Request
from flask import current_app, request
from flask.views import View

from pait.app.base import BaseAppHelper
from pait.app.flask._attribute import get_app_attribute
from pait.app.flask.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[_Request, RequestExtend]):
    CbvType = (View,)
    app_name = "flask"

    request_class = Request

    def _get_request(self, args: List[Any]) -> _Request:
        return request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        return get_app_attribute(current_app, key, default)
