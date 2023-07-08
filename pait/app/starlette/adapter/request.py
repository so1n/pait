from typing import Any, Coroutine, Dict, List, Mapping, Optional

from starlette.datastructures import FormData, Headers, UploadFile
from starlette.requests import Request as _Request

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend
from pait.util import LazyProperty


class RequestExtend(BaseRequestExtend[_Request]):
    @property
    def scheme(self) -> str:
        return self.request.url.scheme

    @property
    def path(self) -> str:
        return self.request.url.path

    @property
    def hostname(self) -> str:
        if self.request.url.port:
            return f"{self.request.url.hostname}:{self.request.url.port}"
        return self.request.url.hostname


class Request(BaseRequest[_Request, RequestExtend]):
    RequestType = _Request
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers

    def __init__(self, request: _Request, args: List[Any], kwargs: Mapping[str, Any]):
        super().__init__(request, args, kwargs)
        self._form: Optional[FormData] = None

    def request_extend(self) -> RequestExtend:
        return RequestExtend(self.request)

    def body(self) -> Coroutine[Any, Any, dict]:
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
        @LazyProperty(self)
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
        @LazyProperty(self)
        async def _multiform() -> Dict[str, List[Any]]:
            form_data: FormData = await self.get_form()
            return {
                key: [i for i in form_data.getlist(key) if not isinstance(i, UploadFile)]
                for key, _ in form_data.items()
            }

        return _multiform()

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.query_params.getlist(key) for key, _ in self.request.query_params.items()}
