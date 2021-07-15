import json
from typing import Any, Dict, List, Mapping, Tuple, Type

from tornado.httputil import RequestStartLine
from tornado.web import RequestHandler

from pait.app.base import BaseAppHelper
from pait.model.response import PaitResponseModel
from pait.util import LazyProperty, gen_example_json_from_schema

__all__ = ["AppHelper"]


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

