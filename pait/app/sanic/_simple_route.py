import re
import string
from typing import Callable

from sanic import Blueprint, Sanic

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.sanic.plugin.unified_response import UnifiedResponsePlugin
from pait.util import get_func_param_kwargs


def replace_openapi_url_to_url(url: str) -> str:
    """Convert the OpenAPI URL format to a format supported by the web framework

    >>> assert "http://google.com/user/<user_id>/abc/<another_id>/def" == replace_openapi_url_to_url(
    >>>    "http://google.com/user/{user_id:int}/abc/{another_id:int}/def"
    >>> )
    """
    matches = re.findall(r"{([a-zA-Z_]+)}", url)
    for match in matches:
        url = url.replace("{" + match + "}", f"<{match}>")
    return url


def add_simple_route(
    app: Sanic,
    simple_route: "SimpleRoute",
    _replace_openapi_url_to_url: Callable[[str], str] = replace_openapi_url_to_url,
) -> None:
    add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_route(
        simple_route.route,
        _replace_openapi_url_to_url(simple_route.url),
        methods=set(simple_route.methods),
        **get_func_param_kwargs(app.add_route, simple_route.kwargs),
    )


def add_multi_simple_route(
    app: Sanic,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    _replace_openapi_url_to_url: Callable[[str], str] = replace_openapi_url_to_url,
) -> None:
    blueprint: Blueprint = Blueprint(
        title.translate(str.maketrans({key: "" for key in string.punctuation})).replace(" ", ""),  # type: ignore
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
        blueprint.add_route(
            simple_route.route, _replace_openapi_url_to_url(simple_route.url), methods=set(simple_route.methods)
        )
    app.blueprint(blueprint)
