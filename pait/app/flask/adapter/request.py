from typing import Any, AsyncGenerator, Dict, Generator, List, Mapping, Union

from flask import Request as FlaskRequest
from flask import request as _request
from werkzeug.datastructures import EnvironHeaders, Headers, ImmutableMultiDict

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
from pait.util import LazyProperty


class RequestExtend(BaseRequestExtend[FlaskRequest]):
    @property
    def scheme(self) -> str:
        return _request.scheme

    @property
    def path(self) -> str:
        return _request.path

    @property
    def hostname(self) -> str:
        return _request.host


class Request(BaseRequest[FlaskRequest, RequestExtend]):
    RequestType = FlaskRequest
    FormType = ImmutableMultiDict
    FileType = FlaskRequest.files
    HeaderType = EnvironHeaders

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> dict:
        return _request.json or {}

    def cookie(self) -> dict:
        return _request.cookies

    def file(self) -> FlaskRequest.files:  # type: ignore
        return _request.files

    def form(self) -> FlaskRequest.form:  # type: ignore
        return _request.form

    def header(self) -> Headers:
        return _request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    def query(self) -> Dict[str, Any]:
        return _request.args

    def stream(self, size: int = -1) -> Union[Generator[bytes, None, None], AsyncGenerator[bytes, None]]:
        while True:
            chunk = _request.stream.read(size)
            if chunk is None:
                break
            yield chunk
        return None

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: _request.form.getlist(key) for key, _ in _request.form.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, List[Any]]:
        return {key: _request.args.getlist(key) for key, _ in _request.args.items()}
