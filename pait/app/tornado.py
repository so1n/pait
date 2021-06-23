import json
from abc import ABC
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type

from tornado.httputil import RequestStartLine
from tornado.web import Application, RequestHandler

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.app.base import BaseAppHelper
from pait.core import PaitCoreModel
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.util import LazyProperty


class AppHelper(BaseAppHelper):
    RequestType = RequestStartLine
    FormType = dict
    FileType = dict
    HeaderType = dict
    app_name = "tornado"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)
        if not self.cbv_class:
            raise RuntimeError("Can not load Tornado handle")

        self.request = self.cbv_class.request
        self.path_kwargs: Dict[str, Any] = self.cbv_class.path_kwargs

    def body(self) -> dict:
        return json.loads(self.request.body.decode())

    def cookie(self) -> dict:
        return self.request.cookies

    def file(self) -> dict:
        return self.request.files

    def form(self) -> dict:
        return {key: value[0] for key, value in self.request.body_arguments}

    def header(self) -> dict:
        return self.request.headers

    def path(self) -> dict:
        return self.path_kwargs

    @LazyProperty()
    def query(self) -> dict:
        return {key: value[0].decode() for key, value in self.request.query_arguments.items()}

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return self.request.body_arguments

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: [i.decode() for i in value] for key, value in self.request.query_arguments.items()}


def load_app(app: Application, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for rule in app.wildcard_router.rules:
        path: str = rule.matcher.regex.pattern  # type: ignore
        base_name: str = rule.target.__name__
        for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
            try:
                handler: Callable = getattr(rule.target, method, None)
            except TypeError:
                continue
            route_name: str = f"{base_name}.{method}"
            pait_id: Optional[str] = getattr(handler, "_pait_id", None)
            if not pait_id:
                continue
            pait_data.add_route_info(AppHelper.app_name, pait_id, path, {method}, route_name, project_name)
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: str = "root",
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


def add_doc_route(
    app: Application,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    class NotFound(Exception):
        pass

    class BaseHandle(RequestHandler, ABC):
        def _handle_request_exception(self, exc: BaseException) -> None:
            self.set_status(404)
            self.write(
                (
                    "The requested URL was not found on the server. If you entered"
                    " the URL manually please check your spelling and try again."
                )
            )
            self.finish()

        def _get_request_pin_code(self) -> Optional[str]:
            r_pin_code: Optional[str] = {
                key: value[0].decode() for key, value in self.request.query_arguments.items()
            }.get("pin_code", None)
            if pin_code:
                if r_pin_code != pin_code:
                    raise NotFound
            return r_pin_code

        def _get_open_json_url(self) -> str:
            r_pin_code: Optional[str] = self._get_request_pin_code()
            openapi_json_url: str = (
                f"http://{self.request.host}{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
            )
            if r_pin_code:
                openapi_json_url += f"?pin_code={r_pin_code}"
            return openapi_json_url

    class GetRedocHtmlHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self.write(_get_redoc_html(self._get_open_json_url(), title))

    class GetSwaggerUiHtmlHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self.write(_get_swagger_ui_html(self._get_open_json_url(), title))

    class OpenApiHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self._get_request_pin_code()
            pait_dict: Dict[str, PaitCoreModel] = load_app(self.application)
            pait_openapi: PaitOpenApi = PaitOpenApi(
                pait_dict,
                title=title,
                open_api_server_list=[{"url": f"http://{self.request.host}", "description": ""}],
                open_api_tag_list=open_api_tag_list,
            )
            self.write(pait_openapi.open_api_dict)

    if not prefix.endswith("/"):
        prefix = prefix + "/"
    app.add_handlers(
        r".*",
        [
            (r"{}redoc".format(prefix), GetRedocHtmlHandle),
            (r"{}swagger".format(prefix), GetSwaggerUiHtmlHandle),
            (r"{}openapi.json".format(prefix), OpenApiHandle),
        ],
    )
