from functools import partial
from typing import Callable, Type, Union

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route
from starlette.requests import Request
from starlette.datastructures import FormData, Headers, UploadFile

from pait.app.base import BaseAsyncAppDispatch
from pait.g import add_to_pait_name_dict
from pait.lazy_property import LazyAsyncProperty, LazyProperty
from pait.verify import params_verify as _params_verify


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


def load_app(app: Starlette):
    for route in app.routes:
        if not isinstance(route, Route):
            # not support
            continue
        path: str = route.path
        method_set: set = route.methods
        route_name: str = route.name
        endpoint: Union[Callable, Type] = route.endpoint
        pait_id: str = getattr(route.endpoint, '_pait_id', None)
        if not pait_id and issubclass(endpoint, HTTPEndpoint):
            for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
                method_endpoint = getattr(endpoint, method, None)
                if not method_endpoint:
                    continue
                method_set = {method}
                pait_id = getattr(method_endpoint, '_pait_id', None)
                add_to_pait_name_dict(pait_id, path, method_set, f'{route_name}.{method}', method_endpoint)
        else:
            add_to_pait_name_dict(pait_id, path, method_set, route_name, endpoint)


params_verify = partial(_params_verify, StarletteDispatch)
