import string
from typing import Callable, Optional

from sanic import Blueprint, Sanic

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.sanic.plugin.unified_response import UnifiedResponsePlugin
from pait.util import get_func_param_kwargs

from ._path import path_converter


def default_replace_openapi_url_to_url(url: str) -> str:
    """Convert the OpenAPI URL format to a format supported by the web framework"""
    return path_converter.replace_openapi_url_to_url(url)


def add_simple_route(
    app: Sanic,
    simple_route: "SimpleRoute",
    replace_openapi_url_to_url: Callable[[str], str] = default_replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
) -> None:
    if auto_add_unified_response_plugin:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_route(
        simple_route.route,
        replace_openapi_url_to_url(simple_route.url),
        methods=set(simple_route.methods),
        **get_func_param_kwargs(app.add_route, simple_route.kwargs),
    )


def add_multi_simple_route(
    app: Sanic,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    replace_openapi_url_to_url: Callable[[str], str] = default_replace_openapi_url_to_url,
    auto_add_unified_response_plugin: bool = True,
    blueprint: Optional[Blueprint] = None,
) -> None:
    _blueprint: Blueprint = blueprint or Blueprint(
        title.translate(str.maketrans({key: "" for key in string.punctuation})).replace(" ", ""),  # type: ignore
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        if auto_add_unified_response_plugin:
            add_route_plugin(simple_route, UnifiedResponsePlugin)
        _blueprint.add_route(
            simple_route.route, replace_openapi_url_to_url(simple_route.url), methods=set(simple_route.methods)
        )
    if not blueprint:
        app.blueprint(_blueprint)
