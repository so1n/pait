import logging
from typing import Callable, Dict, Set

from flask.app import Flask
from flask.views import MethodView

from pait.data import PaitCoreProxyModel
from pait.g import pait_data
from pait.model.core import PaitCoreModel

from ._app_helper import AppHelper
from ._pait import Pait
from ._pait import pait as default_pait

__all__ = ["load_app", "get_openapi_path"]


def get_openapi_path(path: str) -> str:
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
    return openapi_path


# cover
def load_app(
    app: Flask,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}

    for route in app.url_map.iter_rules():
        if route.endpoint == "static":
            continue
        path: str = route.rule
        method_set: Set[str] = route.methods or set()
        route_name: str = route.endpoint
        endpoint: Callable = app.view_functions[route_name]
        pait_id: str = getattr(endpoint, "_pait_id", "")
        # replace path <xxx> to {xxx}
        openapi_path: str = get_openapi_path(path)
        if not pait_id:
            view_class_endpoint = getattr(endpoint, "view_class", None)
            if not view_class_endpoint or not issubclass(view_class_endpoint, MethodView):
                if auto_load_route:
                    endpoint = pait()(endpoint)
                    pait_id = getattr(endpoint, "_pait_id")
                    app.view_functions[route_name] = endpoint
                    core_model = pait_data.get_core_model(
                        AppHelper.app_name,
                        pait_id,
                        path,
                        openapi_path,
                        method_set,
                        route_name if override_operation_id else "",
                        overwrite_already_exists_data=overwrite_already_exists_data,
                    )
                    if core_model:
                        _pait_data[pait_id] = core_model
                else:
                    logging.warning(
                        f"loan path:{path} fail, endpoint:{endpoint} not `view_class` attributes"
                    )  # pragma: no cover
                continue
            for method in view_class_endpoint.methods:
                method = method.lower()
                method_set = {method}
                cbv_endpoint = getattr(view_class_endpoint, method, None)
                if not cbv_endpoint:
                    continue
                pait_id = getattr(cbv_endpoint, "_pait_id", "")
                if not pait_id:
                    from pait.app.flask import pait

                    endpoint = pait()(cbv_endpoint)
                    pait_id = getattr(endpoint, "_pait_id")
                    setattr(view_class_endpoint, method, endpoint)

                core_model = pait_data.get_core_model(
                    AppHelper.app_name,
                    pait_id,
                    path,
                    openapi_path,
                    method_set,
                    f"{route_name}.{method}" if override_operation_id else "",
                    overwrite_already_exists_data=overwrite_already_exists_data,
                )
                if core_model:
                    if auto_cbv_handle:
                        real_core_model = PaitCoreProxyModel.get_core_model(core_model)
                        real_core_model.param_handler_plugin.check_cbv_handler(real_core_model, view_class_endpoint)
                        real_core_model.param_handler_plugin.add_cbv_prd(
                            real_core_model, view_class_endpoint, real_core_model.param_handler_pm.plugin_kwargs
                        )
                        real_core_model.build()
                    _pait_data[pait_id] = core_model
        else:
            core_model = pait_data.get_core_model(
                AppHelper.app_name,
                pait_id,
                path,
                openapi_path,
                method_set,
                route_name if override_operation_id else "",
                overwrite_already_exists_data=overwrite_already_exists_data,
            )
            if core_model:
                _pait_data[pait_id] = core_model
    return _pait_data
