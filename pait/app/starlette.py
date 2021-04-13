from typing import Any, Callable, Coroutine, Dict, List, Mapping, Optional, Tuple, Type, Union

from starlette.applications import Starlette
from starlette.datastructures import FormData, Headers, UploadFile
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route

from pait.app.base import BaseAppHelper
from pait.core import pait as _pait
from pait.g import pait_data
from pait.model import PaitCoreModel, PaitResponseModel, PaitStatus
from pait.util import LazyProperty


class AppHelper(BaseAppHelper):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers
    app_name = "starlette"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)

    def body(self) -> dict:
        return self.request.json()

    def cookie(self) -> dict:
        return self.request.cookies

    def file(self) -> UploadFile:
        return self.request.form()

    def form(self) -> FormData:
        return self.request.form()

    def header(self) -> Headers:
        return self.request.headers

    def path(self) -> dict:
        return self.request.path_params

    def query(self) -> dict:
        return dict(self.request.query_params)

    @LazyProperty()
    def multiform(self) -> Coroutine[Any, Any, Dict[str, List[Any]]]:
        async def _() -> Dict[str, List[Any]]:
            form_data = await self.request.form()
            return {key: form_data.getlist(key) for key, _ in form_data.items()}

        return _()

    @LazyProperty()
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.query_params.getlist(key) for key, _ in self.request.query_params.items()}


def load_app(app: Starlette) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
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
                if not pait_id:
                    continue
                pait_data.add_route_info(AppHelper.app_name, pait_id, path, method_set, f"{route_name}.{method}")
                _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
        else:
            pait_data.add_route_info(AppHelper.app_name, pait_id, path, method_set, route_name)
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
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
