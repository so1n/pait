import json
from typing import Any, Dict, List, Mapping

from tornado.httputil import HTTPHeaders, HTTPServerRequest

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
from pait.util import LazyProperty


class RequestExtend(BaseRequestExtend[HTTPServerRequest]):
    @property
    def scheme(self) -> str:
        return self.request.protocol

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def hostname(self) -> str:
        return self.request.host


class Request(BaseRequest[HTTPServerRequest, RequestExtend]):
    RequestType = HTTPServerRequest
    FormType = dict
    FileType = dict
    HeaderType = dict

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    @LazyProperty()
    def body(self) -> dict:
        return json.loads(self.request.body.decode())

    @LazyProperty()
    def cookie(self) -> dict:
        return {i.key: i.value for i in self.request.cookies.values()}

    @LazyProperty()
    def file(self) -> dict:
        return {item["filename"]: item for item in self.request.files["file"]}

    @LazyProperty()
    def form(self) -> dict:
        if self.request.arguments:
            form_dict: dict = {key: value[0].decode() for key, value in self.request.arguments.items()}
        else:
            form_dict = json.loads(self.request.body.decode())  # pragma: no cover
        return form_dict

    def header(self) -> HTTPHeaders:
        return self.request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

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
