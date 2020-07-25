from functools import partial
from typing import Mapping

from flask import request, Request
from pait.util import BaseAsyncHelper
from pait.verify import sync_params_verify


class FlaskHelper(BaseAsyncHelper):
    RequestType = None
    FormType = Request.form
    FileType = Request.files

    def __init__(self, _request: None):
        super().__init__(request)

    def header(self) -> Mapping:
        return request.headers

    def cookie(self) -> dict:
        return request.cookies

    def from_(self):
        return request.form

    def file(self):
        return request.files

    def query(self) -> dict:
        return dict(request.args)

    def body(self) -> dict:
        return request.json


params_verify = partial(sync_params_verify, FlaskHelper)
