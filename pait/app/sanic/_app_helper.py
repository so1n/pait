from dataclasses import MISSING
from typing import Any

from sanic.request import Request as _Request
from sanic.views import CompositionView, HTTPMethodView
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseAppHelper
from pait.app.sanic.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[_Request, RequestExtend]):
    CbvType = (HTTPMethodView, CompositionView)
    app_name = "sanic"

    request_class = Request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        if default is MISSING:
            return getattr(self.raw_request.app.ctx, key)
        return getattr(self.raw_request.app.ctx, key, default)
