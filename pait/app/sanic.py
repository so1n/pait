import logging
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type

from sanic.app import Sanic
from sanic.headers import HeaderIterable
from sanic.request import File, Request, RequestParameters
from sanic import Blueprint, HTTPResponse, response

from pait.app.base import BaseAppHelper
from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.open_api import PaitOpenApi
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model import PaitCoreModel, PaitResponseModel, PaitStatus
from pait.util import LazyProperty


class AppHelper(BaseAppHelper):
    RequestType = Request
    FormType = RequestParameters
    FileType = File
    HeaderType = HeaderIterable
    app_name = "sanic"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)

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


def load_app(app: Sanic, project_name: str = "") -> Dict[str, PaitCoreModel]:
    _pait_data: Dict[str, PaitCoreModel] = {}
    """Read data from the route that has been registered to `pait`"""
    for parts, route in app.router.routes_all.items():
        if "static" in route.name:
            continue

        route_name: str = route.name
        for path, handler_dict in route.handlers.items():
            for method, handler_list in handler_dict.items():
                for handler in handler_list:
                    view_class: Optional[Type] = getattr(handler, "view_class", None)
                    if view_class:
                        handler = getattr(view_class, method.lower(), None)
                    if not handler:
                        logging.warning(f"{route_name} can not found handle")
                        continue
                    pait_id: Optional[str] = getattr(handler, "_pait_id", None)
                    if not pait_id:
                        logging.warning(f"{route_name} can not found pait id")
                        continue
                    pait_data.add_route_info(AppHelper.app_name, pait_id, path, {method}, route_name, project_name)
                    _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None,
) -> Callable:
    """Help starlette provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        author=author,
        desc=desc,
        summary=summary,
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
    )


def get_redoc_html(request: Request) -> HTTPResponse:
    return response.html(
        _get_redoc_html(f"http://{request.host}{'/'.join(request.path.split('/')[:-1])}/openapi.json", "test")
    )


def openapi_route(request: Request) -> HTTPResponse:
    pait_dict: Dict[str, PaitCoreModel] = load_app(request.app)
    pait_openapi: PaitOpenApi = PaitOpenApi(
        pait_dict,
        title="Pait Doc",
        open_api_server_list=[
            {"url": f"http://{request.host}", "description": ""}
        ],
        open_api_tag_list=[
            {"name": "test", "description": "test api"},
            {"name": "user", "description": "user api"},
        ],
    )
    return response.json(pait_openapi.open_api_dict)


def add_reddoc_route(app: Sanic, prefix: str = "/") -> None:
    blueprint: Blueprint = Blueprint("api doc", prefix)
    blueprint.add_route(get_redoc_html, "/redoc", methods={"GET"})
    blueprint.add_route(openapi_route, "/openapi.json", methods={"GET"})
    app.blueprint(blueprint)
