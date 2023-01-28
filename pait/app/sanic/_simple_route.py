from typing import Any

from sanic import Blueprint, HTTPResponse, Sanic, json

from pait.app.base.simple_route import MediaTypeEnum, SimpleRoute
from pait.app.base.simple_route import SimpleRoutePlugin as _SimpleRoutePlugin
from pait.app.base.simple_route import add_route_plugin


class SimpleRoutePlugin(_SimpleRoutePlugin):
    def _merge(self, return_value: Any, *args: Any, **kwargs: Any) -> Any:
        if self.media_type is MediaTypeEnum.json.value:
            return json(return_value)
        return HTTPResponse(return_value, headers=self.headers, status=self.status_code, content_type=self.media_type)


def add_simple_route(
    app: Sanic,
    simple_route: SimpleRoute,
) -> None:
    add_route_plugin(simple_route, SimpleRoutePlugin)
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
        add_route_plugin(simple_route, SimpleRoutePlugin)
        blueprint.add_route(simple_route.route, simple_route.url, methods=set(simple_route.methods))
    app.blueprint(blueprint)
