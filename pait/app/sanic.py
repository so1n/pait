import logging
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, Set, Tuple, Type, TypeVar

from sanic import response
from sanic.app import Sanic
from sanic.blueprints import Blueprint
from sanic.exceptions import NotFound
from sanic.headers import HeaderIterable
from sanic.request import File, Request, RequestParameters
from sanic.response import HTTPResponse, json
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.app.base import BaseAppHelper, BaseTestHelper
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.util import LazyProperty, gen_example_json_from_schema


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

    @LazyProperty(is_class_func=True)
    def query(self) -> dict:
        return {key: value[0] for key, value in self.request.args.items()}

    @LazyProperty(is_class_func=True)
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: self.request.form.getlist(key) for key, _ in self.request.form.items()}

    @LazyProperty(is_class_func=True)
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.args.getlist(key) for key, _ in self.request.args.items()}

    @staticmethod
    def make_mock_response(pait_response: Type[PaitResponseModel]) -> HTTPResponse:
        if pait_response.media_type == "application/json" and pait_response.response_data:
            resp: HTTPResponse = json(gen_example_json_from_schema(pait_response.response_data.schema()))
            resp.status = pait_response.status_code[0]
            if pait_response.header:
                resp.headers.update(pait_response.header)
            return resp
        else:
            raise NotImplementedError()


def load_app(app: Sanic, project_name: str = "") -> Dict[str, PaitCoreModel]:
    _pait_data: Dict[str, PaitCoreModel] = {}
    """Read data from the route that has been registered to `pait`"""
    for route in app.router.routes:
        if "static" in route.name:
            continue

        route_name: str = route.name
        method_set: Set[str] = route.methods
        path: str = route.path
        handler: Callable = route.handler

        for method in method_set:
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

        # old version
        # for path, handler_dict in route.handlers.items():
        #     for method, handler_list in handler_dict.items():
        #         for handler in handler_list:
        #             view_class: Optional[Type] = getattr(handler, "view_class", None)
        #             if view_class:
        #                 handler = getattr(view_class, method.lower(), None)
        #             if not handler:
        #                 logging.warning(f"{route_name} can not found handle")
        #                 continue
        #             pait_id: Optional[str] = getattr(handler, "_pait_id", None)
        #             if not pait_id:
        #                 logging.warning(f"{route_name} can not found pait id")
        #                 continue
        #             pait_data.add_route_info(AppHelper.app_name, pait_id, path, {method}, route_name, project_name)
        #             _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


_T = TypeVar("_T", bound=TestingResponse)


class SanicTestHelper(BaseTestHelper, Generic[_T]):
    client: SanicTestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)

    def _assert_response(self, resp: TestingResponse) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.status in response_model.status_code,
                resp.content_type == response_model.media_type,
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**resp.json)
                    check_list.append(True)
                except:
                    check_list.append(False)
            if all(check_list):
                return
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}. resp:{resp}")

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            return self.path_dict[path_str[1:-1]]
        return None

    def _make_response(self, method: str) -> TestingResponse:
        method = method.lower()
        if method == "get":
            request, resp = self.client._sanic_endpoint_test(method, uri=self.path, headers=self.header_dict)
        else:
            request, resp = self.client._sanic_endpoint_test(
                method,
                uri=self.path,
                data=self.form_dict,
                json=self.body_dict,
                headers=self.header_dict,
                files=self.file_dict,
            )
        return resp


def pait(
    # param check
    at_most_one_of_list: Optional[List[List[str]]] = None,
    required_by: Optional[Dict[str, List[str]]] = None,
    # doc
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
) -> Callable:
    """Help starlette provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        author=author,
        desc=desc,
        summary=summary,
        name=name,
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
        at_most_one_of_list=at_most_one_of_list,
        required_by=required_by,
    )


def add_doc_route(
    app: Sanic,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if pin_code:
        logging.info(f"doc route start pin code:{pin_code}")

    def _get_request_pin_code(request: Request) -> Optional[str]:
        r_pin_code: Optional[str] = request.args.get("pin_code", None)
        if pin_code:
            if r_pin_code != pin_code:
                raise NotFound
        return r_pin_code

    def _get_open_json_url(request: Request) -> str:
        r_pin_code: Optional[str] = _get_request_pin_code(request)
        openapi_json_url: str = f"http://{request.host}{'/'.join(request.path.split('/')[:-1])}/openapi.json"
        if r_pin_code:
            openapi_json_url += f"?pin_code={r_pin_code}"
        return openapi_json_url

    def get_redoc_html(request: Request) -> HTTPResponse:
        return response.html(_get_redoc_html(_get_open_json_url(request), title))

    def get_swagger_ui_html(request: Request) -> HTTPResponse:
        return response.html(_get_swagger_ui_html(_get_open_json_url(request), title))

    def openapi_route(request: Request) -> HTTPResponse:
        _get_request_pin_code(request)
        pait_dict: Dict[str, PaitCoreModel] = load_app(request.app)
        pait_openapi: PaitOpenApi = PaitOpenApi(
            pait_dict,
            title=title,
            open_api_server_list=[{"url": f"http://{request.host}", "description": ""}],
            open_api_tag_list=open_api_tag_list,
        )
        return response.json(pait_openapi.open_api_dict)

    blueprint: Blueprint = Blueprint("api doc", prefix)
    blueprint.add_route(get_redoc_html, "/redoc", methods={"GET"})
    blueprint.add_route(get_swagger_ui_html, "/swagger", methods={"GET"})
    blueprint.add_route(openapi_route, "/openapi.json", methods={"GET"})
    app.blueprint(blueprint)
