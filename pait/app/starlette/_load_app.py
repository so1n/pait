import inspect
from typing import Callable, Dict, Type, Union

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route

from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper

__all__ = ["load_app"]


def load_app(app: Starlette, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.routes:
        if not isinstance(route, Route):
            # not support
            continue
        path: str = route.path
        openapi_path: str = path
        method_set: set = route.methods or set()
        route_name: str = route.name
        endpoint: Union[Callable, Type] = route.endpoint
        pait_id: str = getattr(route.endpoint, "_pait_id", None)
        if not pait_id and inspect.isclass(endpoint) and issubclass(endpoint, HTTPEndpoint):  # type: ignore
            for method in ["get", "post", "head", "options", "delete", "put", "trace", "patch"]:
                method_endpoint = getattr(endpoint, method, None)
                if not method_endpoint:
                    continue
                method_set = {method}
                pait_id = getattr(method_endpoint, "_pait_id", None)
                if not pait_id:
                    continue
                pait_data.add_route_info(
                    AppHelper.app_name, pait_id, path, openapi_path, method_set, f"{route_name}.{method}", project_name
                )
                _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
        elif pait_id:
            pait_data.add_route_info(
                AppHelper.app_name, pait_id, path, openapi_path, method_set, route_name, project_name
            )
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data
