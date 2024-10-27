from typing import Any, AsyncGenerator, Dict, Generator, List, Mapping, Union

from sanic import __version__
from sanic.compat import Header
from sanic.request import File
from sanic.request import Request as _Request
from sanic.request import RequestParameters

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
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


class SanicBaseRequest(BaseRequest[_Request, RequestExtend]):
    RequestType = _Request
    FormType = RequestParameters
    FileType = File
    HeaderType = Header

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> dict:
        return self.request.json

    def cookie(self) -> dict:
        return self.request.cookies

    def header(self) -> Header:
        return self.request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    ##################################################
    # sanic return result like: {"a": [1], "b": [2]} #
    # not support raw_return future                  #
    ##################################################
    @LazyProperty()
    def file(self) -> Dict[str, File]:
        return {key: value[0] for key, value in self.request.files.items()}

    @LazyProperty()
    def form(self) -> dict:
        return {key: value[0] for key, value in self.request.form.items()}

    @LazyProperty()
    def query(self) -> dict:
        return {key: value[0] for key, value in self.request.args.items()}

    def stream(self, size: int = -1) -> Union[Generator[bytes, None, None], AsyncGenerator[bytes, None]]:
        async def _stream() -> AsyncGenerator[bytes, None]:
            while True:
                assert self.request.stream, "Should set `stream=Ture`"
                chunk = await self.request.stream.read()
                if chunk is None:
                    break
                yield chunk

        return _stream()

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: self.request.form.getlist(key) for key, _ in self.request.form.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.args.getlist(key) for key, _ in self.request.args.items()}


class RequestLt23(SanicBaseRequest): ...


class RequestGt23(SanicBaseRequest):
    @LazyProperty()
    def cookie(self) -> dict:
        return {key: value[0] for key, value in self.request.cookies.items()}


if __version__ >= "23.0.0":
    Request = RequestGt23
else:
    Request = RequestLt23  # type: ignore
