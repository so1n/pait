import inspect
import logging
from typing import Any, Callable, Coroutine, Dict, Generic, List, Mapping, Optional, Tuple, Type, TypeVar, Union

from requests import Response as _Response
from starlette.applications import Starlette
from starlette.datastructures import FormData, Headers, UploadFile
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.testclient import TestClient

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
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers
    app_name = "starlette"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)
        self._form: Optional[FormData] = None

    def body(self) -> dict:
        return self.request.json()

    def cookie(self) -> dict:
        return self.request.cookies

    async def get_form(self) -> FormData:
        if self._form:
            return self._form
        form: FormData = await self.request.form()
        self._form = form
        return form

    def file(self) -> Coroutine[Any, Any, FormData]:
        async def _() -> FormData:
            return await self.get_form()

        return _()

    def form(self) -> Coroutine[Any, Any, Dict[str, Any]]:
        @LazyProperty()
        async def _form() -> Dict[str, Any]:
            form_data: FormData = await self.get_form()
            return {key: form_data.getlist(key)[0] for key, _ in form_data.items()}

        return _form()

    def header(self) -> Headers:
        return self.request.headers

    def path(self) -> dict:
        return self.request.path_params

    def query(self) -> dict:
        return dict(self.request.query_params)

    def multiform(self) -> Coroutine[Any, Any, Dict[str, List[Any]]]:
        @LazyProperty()
        async def _multiform() -> Dict[str, List[Any]]:
            form_data: FormData = await self.get_form()
            return {
                key: [i for i in form_data.getlist(key) if not isinstance(i, UploadFile)]
                for key, _ in form_data.items()
            }

        return _multiform()

    @LazyProperty(is_class_func=True)
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.query_params.getlist(key) for key, _ in self.request.query_params.items()}

    @staticmethod
    def make_mock_response(pait_response: Type[PaitResponseModel]) -> Response:
        if pait_response.media_type == "application/json" and pait_response.response_data:
            resp: Response = JSONResponse(gen_example_json_from_schema(pait_response.response_data.schema()))
            resp.status_code = pait_response.status_code[0]
            if pait_response.header:
                resp.headers.update(pait_response.header)
            return resp
        else:
            raise NotImplementedError()


def load_app(app: Starlette, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.routes:
        if not isinstance(route, Route):
            # not support
            continue
        path: str = route.path
        method_set: set = route.methods or set()
        route_name: str = route.name
        endpoint: Union[Callable, Type] = route.endpoint
        pait_id: str = getattr(route.endpoint, "_pait_id", None)
        if not pait_id and inspect.isclass(endpoint) and issubclass(endpoint, HTTPEndpoint):  # type: ignore
            for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
                method_endpoint = getattr(endpoint, method, None)
                if not method_endpoint:
                    continue
                method_set = {method}
                pait_id = getattr(method_endpoint, "_pait_id", None)
                if not pait_id:
                    continue
                pait_data.add_route_info(
                    AppHelper.app_name, pait_id, path, method_set, f"{route_name}.{method}", project_name
                )
                _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
        elif pait_id:
            pait_data.add_route_info(AppHelper.app_name, pait_id, path, method_set, route_name, project_name)
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


_T = TypeVar("_T", bound=_Response)


class StarletteTestHelper(BaseTestHelper, Generic[_T]):
    client: TestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)  # type: ignore

    def _assert_response(self, resp: _Response) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.status_code in response_model.status_code,
                resp.headers["content-type"] == response_model.media_type,
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**resp.json())
                    check_list.append(True)
                except:
                    check_list.append(False)
            if all(check_list):
                return
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}. resp:{resp}")

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "{" and path_str[-1] == "}":
            return self.path_dict[path_str[1:-1]]
        return None

    def _make_response(self, method: str) -> _Response:
        method = method.upper()
        resp: _Response = self.client.request(
            method,
            url=self.path,
            cookies=self.cookie_dict,
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
    app: Starlette,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if pin_code:
        logging.info(f"doc route start pin code:{pin_code}")

    def _get_request_pin_code(request: Request) -> Optional[str]:
        r_pin_code: Optional[str] = request.query_params.get("pin_code", None)
        if pin_code:
            if r_pin_code != pin_code:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "The requested URL was not found on the server. If you entered"
                        " the URL manually please check your spelling and try again."
                    ),
                )
        return r_pin_code

    def _get_open_json_url(request: Request) -> str:
        r_pin_code: Optional[str] = _get_request_pin_code(request)
        openapi_json_url: str = (
            f"http://{request.url.hostname}:{request.url.port}{'/'.join(request.url.path.split('/')[:-1])}/openapi.json"
        )
        if r_pin_code:
            openapi_json_url += f"?pin_code={r_pin_code}"
        return openapi_json_url

    def get_redoc_html(request: Request) -> HTMLResponse:
        return HTMLResponse(_get_redoc_html(_get_open_json_url(request), title))

    def get_swagger_ui_html(request: Request) -> HTMLResponse:
        return HTMLResponse(_get_swagger_ui_html(_get_open_json_url(request), title))

    def openapi_route(request: Request) -> JSONResponse:
        _get_request_pin_code(request)
        pait_dict: Dict[str, PaitCoreModel] = load_app(request.app)
        pait_openapi: PaitOpenApi = PaitOpenApi(
            pait_dict,
            title=title,
            open_api_server_list=[{"url": f"http://{request.url.hostname}:{request.url.port}", "description": ""}],
            open_api_tag_list=open_api_tag_list,
        )
        return JSONResponse(pait_openapi.open_api_dict)

    route: Mount = Mount(
        prefix,
        name="api doc",
        routes=[
            Route("/redoc", get_redoc_html, methods=["GET"]),
            Route("/swagger", get_swagger_ui_html, methods=["GET"]),
            Route("/openapi.json", openapi_route, methods=["GET"]),
        ],
    )
    app.routes.append(route)
