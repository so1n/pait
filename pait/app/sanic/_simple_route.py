import string

from sanic import Blueprint, Sanic

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.sanic.plugin.unified_response import UnifiedResponsePlugin


def add_simple_route(
    app: Sanic,
    simple_route: "SimpleRoute",
) -> None:
    add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_route(simple_route.route, simple_route.url, methods=set(simple_route.methods))


def add_multi_simple_route(
    app: Sanic,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
) -> None:
    blueprint: Blueprint = Blueprint(
        title.translate(str.maketrans({key: "" for key in string.punctuation})).replace(" ", ""),  # type: ignore
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
        blueprint.add_route(simple_route.route, simple_route.url, methods=set(simple_route.methods))
    app.blueprint(blueprint)
