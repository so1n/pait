import functools
import inspect
import logging
from typing import Callable, Dict, Optional, Type, Union

from starlette import routing
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint

from pait.data import PaitCoreProxyModel
from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.util import http_method_tuple

from ._app_helper import AppHelper
from ._pait import Pait
from ._pait import pait as default_pait

__all__ = ["load_app", "get_openapi_path"]


def get_openapi_path(path: str) -> str:
    return path


def _load_route(
    *,
    route: routing.Route,
    _pait_data: Dict[str, PaitCoreModel],
    prefix_path: Optional[str] = None,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> None:
    path: str = route.path
    if prefix_path:
        path = prefix_path + path
    openapi_path: str = get_openapi_path(path)
    method_set: set = route.methods or set()  # type: ignore[has-type]
    route_name: str = route.name
    endpoint: Union[Callable, Type] = route.endpoint
    pait_id: str = getattr(route.endpoint, "_pait_id", "")
    if not pait_id and inspect.isclass(endpoint) and issubclass(endpoint, HTTPEndpoint):  # type: ignore
        for method in http_method_tuple:
            method_endpoint = getattr(endpoint, method, None)
            if not method_endpoint:
                continue
            method_set = {method}
            pait_id = getattr(method_endpoint, "_pait_id", "")
            if not pait_id:
                if not auto_load_route:
                    logging.warning(f"{route_name}.{method} can not found pait id")  # pragma: no cover

                method_endpoint = pait()(method_endpoint)
                pait_id = getattr(method_endpoint, "_pait_id", "")
                setattr(endpoint, method, method_endpoint)

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
                    real_core_model.param_handler_plugin.check_cbv_handler(real_core_model, endpoint)
                    real_core_model.param_handler_plugin.add_cbv_prd(
                        real_core_model, endpoint, real_core_model.param_handler_pm.plugin_kwargs
                    )
                    real_core_model.build()
                _pait_data[pait_id] = core_model
    elif pait_id:
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
    elif auto_load_route:
        from pait.app.starlette import pait

        endpoint = pait()(endpoint)
        pait_id = getattr(endpoint, "_pait_id", "")

        route.endpoint = endpoint
        endpoint_handler = endpoint
        while isinstance(endpoint_handler, functools.partial):
            endpoint_handler = endpoint_handler.func
        if inspect.isfunction(endpoint_handler) or inspect.ismethod(endpoint_handler):
            # Endpoint is function or method. Treat it as `func(request) -> response`.
            route.app = routing.request_response(endpoint)
        else:
            # Endpoint is a class. Treat it as ASGI.
            route.app = endpoint

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
        logging.warning(f"{route_name} can not found pait id")  # pragma: no cover


def load_app(
    app: Starlette,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`"""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app.routes:
        if isinstance(route, routing.Route):
            _load_route(
                route=route,
                _pait_data=_pait_data,
                auto_load_route=auto_load_route,
                override_operation_id=override_operation_id,
                overwrite_already_exists_data=overwrite_already_exists_data,
                pait=pait,
                auto_cbv_handle=auto_cbv_handle,
            )
        elif isinstance(route, routing.Mount):
            for sub_route in route.routes:
                _load_route(
                    route=sub_route,  # type: ignore
                    _pait_data=_pait_data,
                    prefix_path=route.path,
                    auto_load_route=auto_load_route,
                    override_operation_id=override_operation_id,
                    overwrite_already_exists_data=overwrite_already_exists_data,
                    pait=pait,
                    auto_cbv_handle=auto_cbv_handle,
                )
        else:
            logging.warning(f"load_app func not support route:{route.__class__}")

    return _pait_data
