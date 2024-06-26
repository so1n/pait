from typing import Callable

from starlette.applications import Starlette

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.starlette.plugin.unified_response import UnifiedResponsePlugin
from pait.util import get_func_param_kwargs


def add_simple_route(
    app: Starlette,
    simple_route: "SimpleRoute",
    prefix: str = "/",
    replace_openapi_url_to_url: Callable[[str], str] = lambda x: x,
    auto_add_unified_response_plugin: bool = True,
) -> None:
    if auto_add_unified_response_plugin:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
    url: str = prefix + simple_route.url
    url = url.replace("//", "/")
    app.add_route(
        replace_openapi_url_to_url(url),
        simple_route.route,
        methods=simple_route.methods,
        **get_func_param_kwargs(app.add_route, simple_route.kwargs),
    )


def add_multi_simple_route(
    app: Starlette,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",  # Older versions of Starlette do not support routing groups, so this parameter is invalid
    replace_openapi_url_to_url: Callable[[str], str] = lambda x: x,
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
