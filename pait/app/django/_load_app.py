import inspect
import logging
from typing import Callable, Dict, Iterable, Set, Type, Union

from django.urls.resolvers import RegexPattern, RoutePattern, URLPattern, URLResolver
from django.views import View

from pait.data import PaitCoreProxyModel
from pait.g import pait_data
from pait.model.core import PaitCoreModel
from pait.util import http_method_tuple

from ._app_helper import AppHelper
from ._pait import Pait
from ._pait import pait as default_pait
from ._path import path_converter

__all__ = ["load_app", "get_openapi_path"]

_http_method_set = {method.upper() for method in http_method_tuple}


def get_openapi_path(path: str) -> str:
    return path_converter.get_openapi_path(path)


def _get_pattern_path(pattern: Union[RegexPattern, RoutePattern]) -> str:
    route = getattr(pattern, "_route", None)
    if route is not None:
        return route
    regex = pattern.regex.pattern
    regex = regex.lstrip("^").rstrip("$")
    return regex


def _join_path(prefix_path: str, path: str) -> str:
    return (prefix_path.rstrip("/") + "/" + path.lstrip("/")).strip("/")


def _get_route_name(route: URLPattern, path: str) -> str:
    if route.name:
        return str(route.name)
    callback = route.callback
    view_class = getattr(callback, "view_class", None)
    if view_class:
        return view_class.__name__
    return getattr(callback, "__name__", path.replace("/", ".") or "django_route")


def _normalize_method_set(method_iterable: object) -> Set[str]:
    if not isinstance(method_iterable, (list, tuple, set, frozenset)):
        return set()
    return {str(method).upper() for method in method_iterable if str(method).upper() in _http_method_set}


def _get_require_http_methods(callback: Callable) -> Set[str]:
    if not getattr(callback, "__wrapped__", None):
        return set()
    for cell in getattr(callback, "__closure__", None) or ():
        try:
            method_set = _normalize_method_set(cell.cell_contents)
        except ValueError:
            continue
        if method_set:
            return method_set
    return set()


def _get_method_set(callback: Callable) -> Set[str]:
    method_set = getattr(callback, "_pait_method_set", None)
    if method_set:
        return _normalize_method_set(method_set)
    require_http_method_set = _get_require_http_methods(callback)
    if require_http_method_set:
        return require_http_method_set
    view_class = getattr(callback, "view_class", None) or getattr(callback, "cls", None)
    if view_class:
        method_name_set = _normalize_method_set(getattr(view_class, "http_method_names", []))
        return {method for method in method_name_set if hasattr(view_class, method.lower())}
    methods = getattr(callback, "http_method_names", None)
    if methods:
        return _normalize_method_set(methods)
    actions = getattr(callback, "actions", None)
    if actions:
        return _normalize_method_set(actions.keys())
    return {"GET"}


def _load_func_route(
    *,
    route: URLPattern,
    path: str,
    _pait_data: Dict[str, PaitCoreModel],
    auto_load_route: bool,
    override_operation_id: bool,
    overwrite_already_exists_data: bool,
    pait: Pait,
) -> None:
    callback = route.callback
    route_name = _get_route_name(route, path)
    pait_id = getattr(callback, "_pait_id", "")
    if not pait_id:
        if auto_load_route:
            callback = pait()(callback)
            pait_id = getattr(callback, "_pait_id", "")
            route._callback = callback
        else:
            logging.warning(f"{route_name} can not found pait id")  # pragma: no cover
            return

    core_model = pait_data.get_core_model(
        AppHelper.app_name,
        pait_id,
        path,
        get_openapi_path(path),
        _get_method_set(callback),
        route_name if override_operation_id else "",
        overwrite_already_exists_data=overwrite_already_exists_data,
    )
    if core_model:
        _pait_data[pait_id] = core_model


def _load_cbv_route(
    *,
    route: URLPattern,
    path: str,
    view_class: Type[View],
    _pait_data: Dict[str, PaitCoreModel],
    auto_load_route: bool,
    override_operation_id: bool,
    overwrite_already_exists_data: bool,
    pait: Pait,
    auto_cbv_handle: bool,
) -> None:
    route_name = _get_route_name(route, path)
    for method in http_method_tuple:
        method_endpoint = getattr(view_class, method, None)
        if not method_endpoint:
            continue
        pait_id = getattr(method_endpoint, "_pait_id", "")
        if not pait_id:
            if not auto_load_route:
                logging.warning(f"{route_name}.{method} can not found pait id")  # pragma: no cover
                continue
            method_endpoint = pait()(method_endpoint)
            pait_id = getattr(method_endpoint, "_pait_id", "")
            setattr(view_class, method, method_endpoint)

        core_model = pait_data.get_core_model(
            AppHelper.app_name,
            pait_id,
            path,
            get_openapi_path(path),
            {method},
            f"{route_name}.{method}" if override_operation_id else "",
            overwrite_already_exists_data=overwrite_already_exists_data,
        )
        if core_model:
            if auto_cbv_handle:
                real_core_model = PaitCoreProxyModel.get_core_model(core_model)
                real_core_model.param_handler_plugin.check_cbv_handler(real_core_model, view_class)
                real_core_model.param_handler_plugin.add_cbv_prd(
                    real_core_model, view_class, real_core_model.param_handler_pm.plugin_kwargs
                )
                real_core_model.build()
            _pait_data[pait_id] = core_model


def _load_route(
    *,
    route: Union[URLPattern, URLResolver],
    _pait_data: Dict[str, PaitCoreModel],
    prefix_path: str = "",
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> None:
    path = _join_path(prefix_path, _get_pattern_path(route.pattern))
    if isinstance(route, URLResolver):
        for sub_route in route.url_patterns:
            _load_route(
                route=sub_route,
                _pait_data=_pait_data,
                prefix_path=path,
                auto_load_route=auto_load_route,
                override_operation_id=override_operation_id,
                overwrite_already_exists_data=overwrite_already_exists_data,
                pait=pait,
                auto_cbv_handle=auto_cbv_handle,
            )
        return

    callback = route.callback
    view_class = getattr(callback, "view_class", None)
    if view_class and inspect.isclass(view_class) and issubclass(view_class, View):
        _load_cbv_route(
            route=route,
            path=path,
            view_class=view_class,
            _pait_data=_pait_data,
            auto_load_route=auto_load_route,
            override_operation_id=override_operation_id,
            overwrite_already_exists_data=overwrite_already_exists_data,
            pait=pait,
            auto_cbv_handle=auto_cbv_handle,
        )
    else:
        _load_func_route(
            route=route,
            path=path,
            _pait_data=_pait_data,
            auto_load_route=auto_load_route,
            override_operation_id=override_operation_id,
            overwrite_already_exists_data=overwrite_already_exists_data,
            pait=pait,
        )


def load_app(
    app: Iterable[Union[URLPattern, URLResolver]],
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    pait: Pait = default_pait,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the Django urlpatterns that have been registered to `pait`."""
    _pait_data: Dict[str, PaitCoreModel] = {}
    for route in app:
        if isinstance(route, (URLPattern, URLResolver)):
            _load_route(
                route=route,
                _pait_data=_pait_data,
                auto_load_route=auto_load_route,
                override_operation_id=override_operation_id,
                overwrite_already_exists_data=overwrite_already_exists_data,
                pait=pait,
                auto_cbv_handle=auto_cbv_handle,
            )
        else:
            logging.warning(f"load_app func not support route:{route.__class__}")  # pragma: no cover
    return _pait_data
