import logging
from typing import Any, Callable, Dict, List, Mapping, Optional, Set, Tuple, Type

from flask import Flask, Request, request  # type: ignore
from flask.views import MethodView
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAppHelper
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model import PaitCoreModel, PaitResponseModel, PaitStatus
from pait.util import LazyProperty


class AppHelper(BaseAppHelper):
    RequestType = Request
    FormType = ImmutableMultiDict
    FileType = Request.files
    HeaderType = EnvironHeaders
    app_name = "flask"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)

        self.request = request

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


def load_app(app: Flask) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.url_map.iter_rules():
        path: str = route.rule
        method_set: Set[str] = route.methods
        route_name: str = route.endpoint
        endpoint: Callable = app.view_functions[route_name]
        pait_id: Optional[str] = getattr(endpoint, "_pait_id", None)
        if not pait_id:
            if route_name == "static":
                continue
            view_class_endpoint = getattr(endpoint, "view_class", None)
            if not view_class_endpoint or not issubclass(view_class_endpoint, MethodView):
                logging.warning(f"loan path:{path} fail, endpoint:{endpoint} not `view_class` attributes")
                continue
            for method in view_class_endpoint.methods:
                method = method.lower()
                method_set = {method}
                endpoint = getattr(view_class_endpoint, method, None)
                if not endpoint:
                    continue
                pait_id = getattr(endpoint, "_pait_id", None)
                if not pait_id:
                    continue
                pait_data.add_route_info(AppHelper.app_name, pait_id, path, method_set, f"{route_name}.{method}")
                _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
        else:
            pait_data.add_route_info(AppHelper.app_name, pait_id, path, method_set, route_name)
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None,
) -> Callable:
    """Help flask provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        author=author,
        desc=desc,
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
    )
