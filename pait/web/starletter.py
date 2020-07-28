from functools import partial


from starlette.requests import Request
from starlette.datastructures import FormData, UploadFile

from pait.lazy_property import LazyAsyncProperty, LazyProperty
from pait.web.base import BaseAsyncWebDispatch
from pait.verify import async_params_verify


class StarletteDispatch(BaseAsyncWebDispatch):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile

    @LazyAsyncProperty
    async def body(self) -> dict:
        return await self.request.json()

    def cookie(self) -> dict:
        return self.request.cookies

    @LazyAsyncProperty
    async def file(self):
        return await self.request.form()["upload_file"]

    @LazyAsyncProperty
    async def form(self):
        return await self.request.form()

    def header(self) -> dict:
        return self.request.headers

    def path(self) -> dict:
        return self.request.path_params

    @LazyProperty
    def query(self) -> dict:
        return dict(self.request.query_params)


params_verify = partial(async_params_verify, StarletteDispatch)
