import json
from typing import Any, AsyncGenerator, Dict, Generator, List, Mapping, Union

from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, QueryDict
from django.http.request import HttpHeaders

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
from pait.util import LazyProperty


class RequestExtend(BaseRequestExtend[HttpRequest]):
    @property
    def scheme(self) -> str:
        return self.request.scheme

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def hostname(self) -> str:
        return self.request.get_host()


class Request(BaseRequest[HttpRequest, RequestExtend]):
    RequestType = HttpRequest
    FormType = QueryDict
    FileType = UploadedFile
    HeaderType = HttpHeaders

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> Any:
        if not self.request.body:
            return {}
        try:
            return json.loads(self.request.body.decode(self.request.encoding or "utf-8"))
        except ValueError:
            return {}

    def cookie(self) -> dict:
        return self.request.COOKIES

    def file(self) -> Any:
        return self.request.FILES

    def form(self) -> QueryDict:
        return self.request.POST

    def header(self) -> HttpHeaders:
        return self.request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    def query(self) -> dict:
        return self.request.GET.dict()

    def stream(self, size: int = -1) -> Union[Generator[bytes, None, None], AsyncGenerator[bytes, None]]:
        if size <= 0:
            size = 64
        while True:
            chunk = self.request.read(size)
            if not chunk:
                break
            yield chunk
        return None

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: self.request.POST.getlist(key) for key, _ in self.request.POST.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, List[Any]]:
        return {key: self.request.GET.getlist(key) for key, _ in self.request.GET.items()}
