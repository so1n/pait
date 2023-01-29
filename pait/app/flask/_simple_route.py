from flask import Blueprint, Flask

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.flask.plugin.unified_response import UnifiedResponsePlugin

__all__ = ["SimpleRoute", "add_simple_route", "add_multi_simple_route"]


def add_simple_route(
    app: Flask,
    simple_route: "SimpleRoute",
) -> None:
    add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_url_rule(simple_route.url, view_func=simple_route.route, methods=simple_route.methods)


def add_multi_simple_route(
    app: Flask,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    import_name: str = "",
) -> None:
    blueprint: Blueprint = Blueprint(
        title,
        import_name=import_name,
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        add_route_plugin(simple_route, UnifiedResponsePlugin)
        blueprint.add_url_rule(simple_route.url, view_func=simple_route.route, methods=simple_route.methods)
    app.register_blueprint(blueprint)
