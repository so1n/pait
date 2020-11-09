from functools import partial
from typing import Any, Dict, Mapping, Tuple

from flask import request, Request
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAsyncAppDispatch
from pait.verify import sync_params_verify


class FlaskDispatch(BaseAsyncAppDispatch):
    RequestType = Request
    FormType = ImmutableMultiDict
    FileType = Request.files
    HeaderType = EnvironHeaders

    def __init__(
        self,
        class_: Any,
        args: Tuple[Any, ...],
        kwargs: Mapping[str, Any]
    ):
        super().__init__(class_, args, kwargs)

        self.request = request
        self.path_dict: Dict[str, Any] = {}
        self.path_dict.update(self.request_kwargs)

    def body(self) -> dict:
        return request.json

    def cookie(self) -> dict:
        return request.cookies

    def file(self) -> Request.files:
        return request.files

    def form(self) -> Request.form:
        return request.form

    def header(self) -> Request.headers:
        return request.headers

    def path(self) -> Dict[str, Any]:
        return self.path_dict

    def query(self) -> dict:
        return dict(request.args)


params_verify = partial(sync_params_verify, FlaskDispatch)
