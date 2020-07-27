from functools import partial
from typing import Mapping

from flask import request, Request
from pait.web.base import BaseAsyncHelper
from pait.verify import sync_params_verify


class FlaskHelper(BaseAsyncHelper):
    RequestType = Request
    FormType = Request.form
    FileType = Request.files

    def __init__(self, _request: None):
        super().__init__(request)

    def body(self) -> dict:
        return request.json

    def cookie(self) -> dict:
        return request.cookies

    def file(self):
        return request.files

    def from_(self):
        return request.form

    def header(self) -> Mapping:
        return request.headers

    def query(self) -> dict:
        return dict(request.args)


params_verify = partial(sync_params_verify, FlaskHelper)
