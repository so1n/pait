import re
from typing import Callable, Optional

from flask.app import Flask
from flask.blueprints import Blueprint

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.flask.plugin.unified_response import UnifiedResponsePlugin
from pait.util import get_func_param_kwargs

__all__ = ["SimpleRoute", "add_simple_route", "add_multi_simple_route", "default_replace_openapi_url_to_url"]


def default_replace_openapi_url_to_url(url: str) -> str:
    """Convert the OpenAPI URL format to a format supported by the web framework

    >>> assert "http://google.com/user/{user_id}/post" == default_replace_openapi_url_to_url(
    >>>    "http://google.com/user/<path:user_id>/post"
    >>> )
    """
    matches = re.findall(r"{([a-zA-Z_]+)}", url)
    for match in matches:
        url = url.replace(f"{{{match}}}", f"<path:{match}>")
    return url


def add_simple_route(
    app: Flask,
    simple_route: "SimpleRoute",
    replace_openapi_url_to_url: Callable[[str], str] = default_replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
) -> None:
    if auto_add_unified_response_plugin:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_url_rule(
        replace_openapi_url_to_url(simple_route.url),
        view_func=simple_route.route,
        methods=simple_route.methods,
        **get_func_param_kwargs(app.add_url_rule, simple_route.kwargs),
    )


def add_multi_simple_route(
    app: Flask,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    import_name: str = "",
    replace_openapi_url_to_url: Callable[[str], str] = default_replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
    blueprint: Optional[Blueprint] = None,
) -> None:
    _blueprint: Blueprint = blueprint or Blueprint(
        title,
        import_name=import_name,
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        if auto_add_unified_response_plugin:
            add_route_plugin(simple_route, UnifiedResponsePlugin)
        _blueprint.add_url_rule(
            replace_openapi_url_to_url(simple_route.url), view_func=simple_route.route, methods=simple_route.methods
        )
    if not blueprint:
        app.register_blueprint(_blueprint)
