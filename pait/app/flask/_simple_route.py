from typing import Any

from flask import Blueprint, Flask

from pait.app.base.simple_route import MediaTypeEnum, SimpleRoute
from pait.app.base.simple_route import SimpleRoutePlugin as _SimpleRoutePlugin
from pait.app.base.simple_route import add_route_plugin

__all__ = ["SimpleRoute", "MediaTypeEnum", "add_route_plugin", "add_multi_simple_route"]


class SimpleRoutePlugin(_SimpleRoutePlugin):
    def _merge(self, return_value: Any, *args: Any, **kwargs: Any) -> Any:
        return return_value


def add_simple_route(
    app: Flask,
    simple_route: SimpleRoute,
) -> None:
    add_route_plugin(simple_route, SimpleRoutePlugin)
    app.add_url_rule(simple_route.url, view_func=simple_route.route, methods=simple_route.methods)


def add_multi_simple_route(
    app: Flask,
    *simple_route_list: SimpleRoute,
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
        add_route_plugin(simple_route, SimpleRoutePlugin)
        blueprint.add_url_rule(simple_route.url, view_func=simple_route.route, methods=simple_route.methods)
    app.register_blueprint(blueprint)
