from dataclasses import MISSING
from typing import Any, Dict, List, Mapping

from sanic.headers import HeaderIterable
from sanic.request import File, Request, RequestParameters
from sanic.views import CompositionView, HTTPMethodView
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseAppHelper, BaseRequestExtend
from pait.util import LazyProperty

__all__ = ["AppHelper", "RequestExtend"]


class RequestExtend(BaseRequestExtend[Request]):
    @property
    def scheme(self) -> str:
        return self.request.scheme

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def hostname(self) -> str:
        return self.request.host


class AppHelper(BaseAppHelper[Request, RequestExtend]):
    RequestType = Request
    FormType = RequestParameters
    FileType = File
    HeaderType = HeaderIterable
    CbvType = (HTTPMethodView, CompositionView)
    app_name = "sanic"

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        if default is MISSING:
            return getattr(self.request.app.ctx, key)
        return getattr(self.request.app.ctx, key, default)

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> dict:
        return self.request.json

    def cookie(self) -> dict:
        return self.request.cookies

    def file(self) -> Dict[str, File]:
        return {key: value[0] for key, value in self.request.files.items()}

    def form(self) -> dict:
        return {key: value[0] for key, value in self.request.form.items()}

    def header(self) -> HeaderIterable:
        return self.request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    @LazyProperty()
    def query(self) -> dict:
        return {key: value[0] for key, value in self.request.args.items()}

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: self.request.form.getlist(key) for key, _ in self.request.form.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.args.getlist(key) for key, _ in self.request.args.items()}
