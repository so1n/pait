import asyncio
from typing import Any, Optional, Type

from tornado.routing import _RuleList
from tornado.web import AnyMatches, Application, RequestHandler, Rule, _ApplicationRouter

from pait.app.base.simple_route import MediaTypeEnum, SimpleRoute
from pait.app.tornado.plugin.base import JsonProtocol
from pait.model.core import PaitCoreModel

__all__ = ["MediaTypeEnum", "SimpleRoute", "add_simple_route", "add_multi_simple_route"]


class SimpleRoutePlugin(JsonProtocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super(SimpleRoutePlugin, self).__call__(*args, **kwargs)
        if asyncio.iscoroutine(response):
            response = await response
        tornado_handle: RequestHandler = args[0]
        return self.gen_response(tornado_handle, response)


def _add_route(
    app: Application,
    request_handler: Type[RequestHandler],
    *simple_route_list: "SimpleRoute",
    prefix: str = "",
    title: str = "",
) -> None:

    rule_list: _RuleList = []
    for simple_route in simple_route_list:
        pait_core_model: Optional["PaitCoreModel"] = getattr(simple_route.route, "pait_core_model", None)
        if not pait_core_model:
            raise RuntimeError(f"{simple_route.route} must be a routing function decorated with pait")
        pait_core_model.add_plugin([SimpleRoutePlugin.build(content_type=simple_route.media_type_enum.value)], [])

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
