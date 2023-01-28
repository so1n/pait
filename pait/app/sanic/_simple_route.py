from sanic import Blueprint, Sanic

from pait.app.base.simple_route import SimpleRoute


def add_simple_route(
    app: Sanic,
    simple_route: SimpleRoute,
) -> None:
    app.add_route(simple_route.route, simple_route.url, methods=set(simple_route.methods))


def add_multi_simple_route(
    app: Sanic,
    *simple_route_list: SimpleRoute,
    prefix: str = "/",
    title: str = "",
) -> None:
    blueprint: Blueprint = Blueprint(
        title,
        url_prefix=prefix,
    )
    for simple_route in simple_route_list:
        blueprint.add_route(simple_route.route, simple_route.url, methods=set(simple_route.methods))
    app.blueprint(blueprint)
