import logging
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type

from sanic.app import Sanic
from sanic.headers import HeaderIterable
from sanic.request import File, Request, RequestParameters

from pait.app.base import BaseAppHelper
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model import PaitResponseModel, PaitStatus
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

    def file(self) -> File:
        return self.request.files

    def form(self) -> RequestParameters:
        return self.request.form

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


def load_app(app: Sanic) -> str:
    """Read data from the route that has been registered to `pait`"""
    for parts, route in app.router.routes_all.items():
        if route.name and "static" in route.name:
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
                    pait_data.add_route_info(AppHelper.app_name, pait_id, path, {method}, route_name)
    return AppHelper.app_name


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
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
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
    )
