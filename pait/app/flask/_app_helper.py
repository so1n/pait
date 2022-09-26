from dataclasses import MISSING
from typing import Any, Dict, List, Mapping

from flask import Request, g, request
from flask.views import View
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAppHelper, BaseRequestExtend
from pait.util import LazyProperty

__all__ = ["AppHelper", "RequestExtend"]


class RequestExtend(BaseRequestExtend[Request]):
    @property
    def scheme(self) -> str:
        return request.scheme

    @property
    def path(self) -> str:
        return request.path

    @property
    def hostname(self) -> str:
        return request.host


class AppHelper(BaseAppHelper[Request, RequestExtend]):

    RequestType = Request
    FormType = ImmutableMultiDict
    FileType = Request.files
    HeaderType = EnvironHeaders
    CbvType = (View,)
    app_name = "flask"

    def __init__(self, args: List[Any], kwargs: Mapping[str, Any]):
        super().__init__(args, kwargs)

        self.request = request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        if default is MISSING:
            return getattr(g, key)
        return getattr(g, key, default)

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> dict:
        return request.json

    def cookie(self) -> dict:
        return request.cookies

    def file(self) -> Request.files:  # type: ignore
        return request.files

    def form(self) -> Request.form:  # type: ignore
        return request.form

    def header(self) -> EnvironHeaders:
        return request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    def query(self) -> Dict[str, Any]:
        return request.args

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: request.form.getlist(key) for key, _ in request.form.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, List[Any]]:
        return {key: request.args.getlist(key) for key, _ in request.args.items()}
