import json
from typing import Any, Dict, List, Mapping

from tornado.httputil import RequestStartLine

from pait.app.base import BaseAppHelper
from pait.util import LazyProperty

__all__ = ["AppHelper"]


class AppHelper(BaseAppHelper):
    RequestType = RequestStartLine
    FormType = dict
    FileType = dict
    HeaderType = dict
    app_name = "tornado"

    def __init__(self, class_: Any, args: List[Any], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)
        if not self.cbv_instance:
            raise RuntimeError("Can not load Tornado handle")  # pragma: no cover

        self.request = self.cbv_instance.request
        self.path_kwargs: Dict[str, Any] = self.cbv_instance.path_kwargs

    def body(self) -> dict:
        return json.loads(self.request.body.decode())

    def cookie(self) -> dict:
        return self.request.cookies

    def file(self) -> dict:
        return {item["filename"]: item for item in self.request.files["file"]}

    @LazyProperty()
    def form(self) -> dict:
        if self.request.arguments:
            form_dict: dict = {key: value[0].decode() for key, value in self.request.arguments.items()}
        else:
            form_dict = json.loads(self.request.body.decode())  # pragma: no cover
        return {key: value[0] for key, value in form_dict.items()}

    def header(self) -> dict:
        return self.request.headers

    def path(self) -> dict:
        return self.path_kwargs

    @LazyProperty()
    def query(self) -> dict:
        return {key: value[0].decode() for key, value in self.request.query_arguments.items()}

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        if self.request.arguments:
            return {key: [i.decode() for i in value] for key, value in self.request.arguments.items()}
        else:
            return {key: [value] for key, value in json.loads(self.request.body.decode()).items()}  # pragma: no cover

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: [i.decode() for i in value] for key, value in self.request.query_arguments.items()}
