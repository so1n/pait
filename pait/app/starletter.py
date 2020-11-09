from functools import partial


from starlette.requests import Request
from starlette.datastructures import FormData, Headers, UploadFile

from pait.lazy_property import LazyAsyncProperty, LazyProperty
from pait.app.base import BaseAsyncAppDispatch
from pait.verify import async_params_verify


class StarletteDispatch(BaseAsyncAppDispatch):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers

    @LazyAsyncProperty
    async def body(self) -> dict:
        return await self.request.json()

    def cookie(self) -> dict:
        return self.request.cookies

    @LazyAsyncProperty
    async def file(self) -> UploadFile:
        return await self.request.form()["upload_file"]

    @LazyAsyncProperty
    async def form(self) -> FormData:
        return await self.request.form()

    def header(self) -> Headers:
        return self.request.headers

    def path(self) -> dict:
        return self.request.path_params

    @LazyProperty
    def query(self) -> dict:
        return dict(self.request.query_params)


params_verify = partial(async_params_verify, StarletteDispatch)
