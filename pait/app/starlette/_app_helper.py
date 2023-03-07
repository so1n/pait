from dataclasses import MISSING
from typing import Any

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request as _Request

from pait.app.base import BaseAppHelper
from pait.app.starlette._attribute import get_app_attribute
from pait.app.starlette.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[_Request, RequestExtend]):
    CbvType = (HTTPEndpoint,)
    app_name = "starlette"

    request_class = Request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        return get_app_attribute(self.raw_request.app, key, default)
