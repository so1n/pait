import logging
from typing import Callable, Dict, Optional, Set

from flask import Flask
from flask.views import MethodView

from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper

__all__ = ["load_app"]


def load_app(app: Flask, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    if not project_name:
        project_name = app.import_name.split(".")[0]
    for route in app.url_map.iter_rules():
        path: str = route.rule
        method_set: Set[str] = route.methods
        route_name: str = route.endpoint
        endpoint: Callable = app.view_functions[route_name]
        pait_id: Optional[str] = getattr(endpoint, "_pait_id", None)
        # replace path <xxx> to {xxx}
        openapi_path: str = path
        if "<" in openapi_path and ">" in openapi_path:
            new_path_list: list = []
            for sub_path in openapi_path.split("/"):
                if not sub_path:
                    continue
                if sub_path[0] == "<" and sub_path[-1] == ">":
                    real_sub_path: str = sub_path[1:-1]
                    if ":" in real_sub_path:
                        real_sub_path = real_sub_path.split(":")[0]
                    real_sub_path = "{" + real_sub_path + "}"
                else:
                    real_sub_path = sub_path
                new_path_list.append(real_sub_path)
            openapi_path = "/".join(new_path_list)
        if not openapi_path.startswith("/"):
            openapi_path = "/" + openapi_path
        if not pait_id:
            if route_name == "static":
                continue
            view_class_endpoint = getattr(endpoint, "view_class", None)
            if not view_class_endpoint or not issubclass(view_class_endpoint, MethodView):
                logging.warning(f"loan path:{path} fail, endpoint:{endpoint} not `view_class` attributes")
                continue
            for method in view_class_endpoint.methods:
                method = method.lower()
                method_set = {method}
                endpoint = getattr(view_class_endpoint, method, None)
                if not endpoint:
                    continue
                pait_id = getattr(endpoint, "_pait_id", None)
                if not pait_id:
                    continue
                pait_data.add_route_info(
                    AppHelper.app_name, pait_id, path, openapi_path, method_set, f"{route_name}.{method}", project_name
                )
                _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
        else:
            pait_data.add_route_info(
                AppHelper.app_name, pait_id, path, openapi_path, method_set, route_name, project_name
            )
            _pait_data[pait_id] = pait_data.get_pait_data(AppHelper.app_name, pait_id)
    return _pait_data
