from typing import Type

from tornado.routing import _RuleList
from tornado.web import AnyMatches, Application, RequestHandler, Rule, _ApplicationRouter

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.tornado.plugin.unified_response import UnifiedResponsePlugin

__all__ = ["SimpleRoute", "add_simple_route", "add_multi_simple_route"]


def _add_route(
    app: Application,
    request_handler: Type[RequestHandler],
    *simple_route_list: "SimpleRoute",
    prefix: str = "",
    title: str = "",
) -> None:
    rule_list: _RuleList = []
    for simple_route in simple_route_list:
        add_route_plugin(simple_route, UnifiedResponsePlugin)

        if title:
            model_str: str = f"{__name__}.{title}.{simple_route.route.__name__}"
        else:
            model_str = f"{__name__}.{simple_route.route.__name__}"
        route_class = type(
            simple_route.route.__name__.title() + "Handler", (request_handler,), {"__model__": model_str}
        )

        for method in simple_route.methods:
            setattr(route_class, method.lower(), simple_route.route)

        url: str = simple_route.url
        if prefix:
            if prefix.endswith("/"):
                prefix = prefix[:-1]
            if simple_route.url.startswith("/"):
                url = simple_route.url[1:]
            url = f"{prefix}/{url}"

        rule_list.append((r"{}".format(url), route_class))

    # Method 1
    # app.add_handlers(r".*$", rule_list)
    #
    # Method 2
    # app.default_router.add_rules(rule_list)
    #
    # Method 3
    app.wildcard_router.add_rules(rule_list)
    app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])


def add_simple_route(
    app: Application, simple_route: "SimpleRoute", request_handler: Type[RequestHandler] = RequestHandler
) -> None:
    _add_route(app, request_handler, simple_route)


def add_multi_simple_route(
    app: Application,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
    request_handler: Type[RequestHandler] = RequestHandler,
) -> None:
    _add_route(app, request_handler, *simple_route_list, prefix=prefix, title=title)
