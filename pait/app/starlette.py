from typing import Callable, List, Optional, Tuple, Type, Union

from starlette.applications import Starlette
from starlette.datastructures import FormData, Headers, UploadFile
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route

from pait.app.base import BaseAsyncAppHelper
from pait.core import pait as _pait
from pait.g import pait_data
from pait.lazy_property import LazyAsyncProperty, LazyProperty
from pait.model import PaitResponseModel, PaitStatus


class AppHelper(BaseAsyncAppHelper):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers

    @LazyAsyncProperty
    async def body(self) -> dict:
        return await self.request.json()

    @LazyProperty
    def cookie(self) -> dict:
        return self.request.cookies

    @LazyAsyncProperty
    async def file(self) -> UploadFile:
        return await self.request.form()["upload_file"]

    @LazyAsyncProperty
    async def form(self) -> FormData:
        return await self.request.form()

    @LazyProperty
    def header(self) -> Headers:
        return self.request.headers

    @LazyProperty
    def path(self) -> dict:
        return self.request.path_params

    @LazyProperty
    def query(self) -> dict:
        return dict(self.request.query_params)


def load_app(app: Starlette) -> None:
    """Read data from the route that has been registered to `pait`"""
    for route in app.routes:
        if not isinstance(route, Route):
            # not support
            continue
        path: str = route.path
        method_set: set = route.methods or set()
        route_name: str = route.name
        endpoint: Union[Callable, Type] = route.endpoint
        pait_id: str = getattr(route.endpoint, "_pait_id", None)
        if not pait_id and issubclass(endpoint, HTTPEndpoint):  # type: ignore
            for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
                method_endpoint = getattr(endpoint, method, None)
                if not method_endpoint:
                    continue
                method_set = {method}
                pait_id = getattr(method_endpoint, "_pait_id", None)
                pait_data.add_route_info(pait_id, path, method_set, f"{route_name}.{method}", method_endpoint)
        else:
            pait_data.add_route_info(pait_id, path, method_set, route_name, endpoint)


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: str = "root",
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None,
) -> Callable:
    """Help starlette provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        author=author,
        desc=desc,
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
    )
