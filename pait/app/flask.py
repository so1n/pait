import logging
from functools import partial
from typing import Any, Dict, Mapping, Tuple

from flask import Flask, request, Request
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAsyncAppDispatch
from pait.g import pait_name_dict
from pait.verify import params_verify as _params_verify


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


def load_app(app: Flask):
    for route in app.url_map.iter_rules():
        path: str = route.rule
        method_set: set = route.methods
        route_name: str = route.endpoint
        endpoint = app.view_functions[route_name]
        pait_name = getattr(endpoint, '_pait_name')
        if not pait_name:
            endpoint.view_class
            get_paitname = getattr(route.endpoint, 'get')
            post_paitname = getattr(route.endpoint, 'post')
        if pait_name in pait_name_dict:
            pait_name_dict[pait_name].path = path
            pait_name_dict[pait_name].method_set = method_set
        else:
            logging.warning(f'loan path:{path} fail, endpoint:{endpoint}')


params_verify = partial(_params_verify, FlaskDispatch)
