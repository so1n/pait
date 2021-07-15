from typing import Any, Dict, List, Mapping, Tuple, Type

from sanic.headers import HeaderIterable
from sanic.request import File, Request, RequestParameters
from sanic.response import HTTPResponse, json
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseAppHelper
from pait.model.response import PaitResponseModel
from pait.util import LazyProperty, gen_example_json_from_schema

__all__ = ["AppHelper"]


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

