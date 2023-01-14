from typing import Any, Dict, List, Mapping, Generic, TypeVar
from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
from sanic.headers import HeaderIterable
from sanic.request import File, Request as _Request, RequestParameters
from pait.util import LazyProperty


class RequestExtend(BaseRequestExtend[_Request]):
    @property
    def scheme(self) -> str:
        return self.request.scheme

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def hostname(self) -> str:
        return self.request.host



class Request(BaseRequest[_Request, RequestExtend]):
    RequestType = _Request
    FormType = RequestParameters
    FileType = File
    HeaderType = HeaderIterable

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

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