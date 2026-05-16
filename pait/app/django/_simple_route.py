from typing import Any, Callable, MutableSequence

from django.urls import path
from django.views.decorators.http import require_http_methods

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.django._path import path_converter
from pait.app.django.plugin.unified_response import UnifiedResponsePlugin
from pait.util import get_func_param_kwargs


def _clean_url(url: str) -> str:
    return url.replace("//", "/").lstrip("/")


def add_simple_route(
    app: MutableSequence[Any],
    simple_route: "SimpleRoute",
    prefix: str = "/",
    replace_openapi_url_to_url: Callable[[str], str] = path_converter.replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
) -> None:
    if auto_add_unified_response_plugin:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
    url = prefix + simple_route.url
    url = _clean_url(replace_openapi_url_to_url(url))
    route_kwargs = get_func_param_kwargs(path, simple_route.kwargs)
    method_set = {method.upper() for method in simple_route.methods}
    route = require_http_methods(list(method_set))(simple_route.route)
    setattr(route, "_pait_method_set", method_set)
    app.append(path(url, route, **route_kwargs))


def add_multi_simple_route(
    app: MutableSequence[Any],
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    replace_openapi_url_to_url: Callable[[str], str] = path_converter.replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
) -> None:
    for simple_route in simple_route_list:
        add_simple_route(
            app,
            simple_route,
            prefix=prefix,
            replace_openapi_url_to_url=replace_openapi_url_to_url,
            auto_add_unified_response_plugin=auto_add_unified_response_plugin,
        )
