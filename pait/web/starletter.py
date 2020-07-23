from functools import partial


from starlette.requests import Request
from starlette.datastructures import FormData, UploadFile

from pait.lazy_property import LazyAsyncProperty, LazyProperty
from pait.util import BaseAsyncHelper
from pait.verify import async_params_verify


class StarletteHelper(BaseAsyncHelper):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile

    def __init__(self, request: Request):
        super().__init__(request)

    def header(self, header_key: str) -> str:
        headers = self.request.headers
        if header_key != header_key.lower():
            value = headers.get(header_key) or headers.get(header_key.lower())
        else:
            value = headers.get(header_key)
        return value

    def cookie(self, key: str) -> str:
        return self.request.cookies[key]

    @LazyAsyncProperty
    async def from_(self):
        return await self.request.form()

    @LazyAsyncProperty
    async def file(self):
        return await self.request.form()["upload_file"]

    @LazyProperty
    def query(self) -> dict:
        return dict(self.request.query_params)

    @LazyAsyncProperty
    async def body(self) -> dict:
        return await self.request.json()


params_verify = partial(async_params_verify, StarletteHelper)
