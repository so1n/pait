import binascii
import json
import os
from abc import ABC
from io import BytesIO
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, Tuple, Type, TypeVar

from tornado.httputil import RequestStartLine
from tornado.testing import AsyncHTTPTestCase, HTTPResponse
from tornado.web import Application, RequestHandler

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
        return {item["filename"]: item for item in self.request.files["file"]}

    @LazyProperty(is_class_func=True)
    def form(self) -> dict:
        if self.request.arguments:
            form_dict: dict = {key: value[0].decode() for key, value in self.request.arguments.items()}
        else:
            form_dict = json.loads(self.request.body.decode())
        return {key: value[0] for key, value in form_dict.items()}

    def header(self) -> dict:
        return self.request.headers

    def path(self) -> dict:
        return self.path_kwargs

    @LazyProperty(is_class_func=True)
    def query(self) -> dict:
        return {key: value[0].decode() for key, value in self.request.query_arguments.items()}

    @LazyProperty(is_class_func=True)
    def multiform(self) -> Dict[str, List[Any]]:
        if self.request.arguments:
            return {key: [i.decode() for i in value] for key, value in self.request.arguments.items()}
        else:
            return {key: [value] for key, value in json.loads(self.request.body.decode()).items()}

    @LazyProperty(is_class_func=True)
    def multiquery(self) -> Dict[str, Any]:
        return {key: [i.decode() for i in value] for key, value in self.request.query_arguments.items()}

    @staticmethod
    def make_mock_response(pait_response: Type[PaitResponseModel]) -> Any:
        tornado_handle: RequestHandler = getattr(pait_response, "handle", None)
        if not tornado_handle:
            raise RuntimeError("Can not load Tornado handle")
        tornado_handle.set_status(pait_response.status_code[0])
        for key, value in pait_response.header.items():
            tornado_handle.set_header(key, value)
        if pait_response.media_type == "application/json" and pait_response.response_data:
            tornado_handle.write(gen_example_json_from_schema(pait_response.response_data.schema()))
            return
        else:
            raise NotImplementedError()


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


_T = TypeVar("_T", bound=HTTPResponse)


class TornadoTestHelper(BaseTestHelper, Generic[_T]):
    client: AsyncHTTPTestCase

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)
        if self.path.endswith("$"):
            self.path = self.path[:-1]

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.get_app())

    def _assert_response(self, resp: HTTPResponse) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.code in response_model.status_code,
                response_model.media_type in resp.headers["Content-Type"],
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**json.loads(resp.body.decode()))
                    check_list.append(True)
                except:
                    check_list.append(False)
            if all(check_list):
                return
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}. resp:{resp}")

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict:
            head_index, tail_index = -1, -1
            for index, i in enumerate(path_str):
                if i == "<":
                    head_index = index
                if i == ">":
                    tail_index = index
            if head_index != -1 or tail_index != -1:
                return self.path_dict[path_str[head_index + 1 : tail_index]]
        return None

    def _make_response(self, method: str) -> HTTPResponse:
        method = method.upper()
        if self.file_dict or self.form_dict:
            if method != "POST":
                raise RuntimeError("Must use method post")
            content_type, body = self.encode_multipart_formdata(data=self.form_dict, files=self.file_dict)
            headers: dict = self.header_dict.copy()
            headers.update({"Content-Type": content_type, "content-length": str(len(body))})
            return self.client.fetch(self.path, method="POST", headers=headers, body=body)
        body_bytes: Optional[bytes] = None
        if self.body_dict:
            body_bytes = json.dumps(self.body_dict).encode()
        return self.client.fetch(self.path, method=method, headers=self.header_dict, body=body_bytes)

    @staticmethod
    def choose_boundary() -> str:
        """
        Our embarrassingly-simple replacement for mimetools.choose_boundary.
        """
        boundary: bytes = binascii.hexlify(os.urandom(16))
        return boundary.decode("ascii")

    def encode_multipart_formdata(self, data: Optional[dict] = None, files: Optional[dict] = None) -> Tuple[str, bytes]:
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
        uploaded as files.
        Return (content_type, body) ready for httplib.HTTP instance
        """
        body: BytesIO = BytesIO()
        boundary: str = self.choose_boundary()
        if data:
            for key, value in data.items():
                body.write(("--%s\r\n" % boundary).encode(encoding="utf-8"))
                body.write(('Content-Disposition:form-data;name="%s"\r\n' % key).encode(encoding="utf-8"))
                body.write("\r\n".encode(encoding="utf-8"))
                if isinstance(value, int):
                    value = str(value)
                body.write(("%s\r\n" % value).encode(encoding="utf-8"))

        if files:
            for key, value in files.items():
                body.write(("--%s\r\n" % boundary).encode(encoding="utf-8"))
                body.write(
                    ('Content-Disposition:form-data;name="file";filename="%s"\r\n' % key).encode(encoding="utf-8")
                )
                body.write("\r\n".encode(encoding="utf-8"))
                body.write(value)
                body.write("\r\n".encode(encoding="utf-8"))

        body.write(("--%s--\r\n" % boundary).encode(encoding="utf-8"))
        content_type: str = "multipart/form-data;boundary=%s" % boundary
        return content_type, body.getvalue()


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
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
        name=name,
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
