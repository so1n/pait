from dataclasses import MISSING
from typing import Any, List, Mapping

from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler

from pait.app.base import BaseAppHelper
from pait.app.tornado._attribute import get_app_attribute
from pait.app.tornado.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[HTTPServerRequest, RequestExtend]):
    CbvType = (RequestHandler,)
    app_name = "tornado"

    request_class = Request

    def __init__(self, args: List[Any], kwargs: Mapping[str, Any]):
        super().__init__(args, kwargs)
        if not self.cbv_instance:
            raise RuntimeError("Can not load Tornado handle")  # pragma: no cover

    def _get_request(self, args: List[Any]) -> HTTPServerRequest:
        return self.cbv_instance.request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        return get_app_attribute(self.cbv_instance.application, key, default)
