import logging
from functools import partial
from typing import Any, Callable, Dict, Mapping, Set, Tuple

from flask import Flask, request, Request
from flask.views import MethodView
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAsyncAppDispatch
from pait.g import add_to_pait_name_dict
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
        method_set: Set[str] = route.methods
        route_name: str = route.endpoint
        endpoint: Callable = app.view_functions[route_name]
        pait_id: str = getattr(endpoint, '_pait_id', None)
        if not pait_id:
            view_class_endpoint = getattr(endpoint, 'view_class', None)
            if route_name == 'static':
                continue
            if not view_class_endpoint or not issubclass(view_class_endpoint, MethodView):
                logging.warning(f'loan path:{path} fail, endpoint:{endpoint} not `view_class` attributes')
                continue
            for method in view_class_endpoint.methods:
                method = method.lower()
                method_set = {method}
                endpoint = getattr(view_class_endpoint, method, None)
                if not endpoint:
                    continue
                pait_id = getattr(endpoint, '_pait_id', None)
                add_to_pait_name_dict(pait_id, path, method_set, f'{route_name}.{method}', endpoint)
        else:
            add_to_pait_name_dict(pait_id, path, method_set, route_name, endpoint)


def params_verify(tag: str = 'root'):
    return _params_verify(FlaskDispatch, tag=tag)
