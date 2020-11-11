import logging
from functools import partial

from starlette.requests import Request
from starlette.datastructures import FormData, Headers, UploadFile

from pait.app.base import BaseAsyncAppDispatch
from pait.g import pait_name_dict
from pait.lazy_property import LazyAsyncProperty, LazyProperty
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


def load_app(app):
    for route in app.routes:
        path: str = route.path
        method_set: set = route.methods
        pait_name: str = getattr(route.endpoint, '_pait_name', None)
        if not pait_name:
            get_paitname = getattr(route.endpoint, 'get')
            post_paitname = getattr(route.endpoint, 'post')
        if pait_name in pait_name_dict:
            pait_name_dict[pait_name].path = path
            pait_name_dict[pait_name].method_set = method_set
        else:
            logging.warning(f'loan path:{path} fail, endpoint:{route.endpoint}')


params_verify = partial(async_params_verify, StarletteDispatch)
