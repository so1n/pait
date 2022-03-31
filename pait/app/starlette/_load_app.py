import inspect
import logging
from typing import Callable, Dict, Optional, Type, Union

from starlette import routing
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint

from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.util import http_method_tuple

from ._app_helper import AppHelper

__all__ = ["load_app"]


def _load_route(
    *, route: routing.Route, _pait_data: Dict[str, PaitCoreModel], project_name: str, prefix_path: Optional[str] = None
) -> None:
    path: str = route.path
    if prefix_path:
        path = prefix_path + path
    openapi_path: str = path
    method_set: set = route.methods or set()
    route_name: str = route.name
    endpoint: Union[Callable, Type] = route.endpoint
    pait_id: str = getattr(route.endpoint, "_pait_id", None)
    if not pait_id and inspect.isclass(endpoint) and issubclass(endpoint, HTTPEndpoint):  # type: ignore
        for method in http_method_tuple:
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
        pait_data.add_route_info(AppHelper.app_name, pait_id, path, openapi_path, method_set, route_name, project_name)
        _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)


def load_app(app: Starlette, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.routes:
        if isinstance(route, routing.Route):
            _load_route(route=route, _pait_data=_pait_data, project_name=project_name)
        elif isinstance(route, routing.Mount):
            for sub_route in route.routes:
                _load_route(
                    route=sub_route,  # type: ignore
                    _pait_data=_pait_data,
                    project_name=project_name,
                    prefix_path=route.path,
                )
        else:
            logging.info(f"load_app func not support route:{route.__class__}")

    return _pait_data
