import asyncio
from contextvars import copy_context
from functools import partial
from typing import Any, Type

from tornado.routing import _RuleList
from tornado.web import AnyMatches, Application, RequestHandler, Rule, _ApplicationRouter

from pait.app.base.simple_route import SimpleRoute
from pait.app.base.simple_route import SimpleRoutePlugin as _SimpleRoutePlugin
from pait.app.base.simple_route import add_route_plugin

__all__ = ["SimpleRoute", "add_simple_route", "add_multi_simple_route"]


class SimpleRoutePlugin(_SimpleRoutePlugin):
    def _merge(self, return_value: Any, *args: Any, **kwargs: Any) -> Any:
        tornado_handle: RequestHandler = args[0]
        tornado_handle.set_status(self.status_code)
        if self.headers is not None:
            for k, v in self.headers.items():
                tornado_handle.set_header(k, v)
        tornado_handle.set_header("Content-Type", self.media_type)
        tornado_handle.write(return_value)
        return return_value

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # Compatible with tornado cannot call sync routing function
        if self._is_async_func:
            return await self._async_call(*args, **kwargs)
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None, partial(copy_context().run, partial(self._call, *args, **kwargs))  # Matryoshka
            )


def _add_route(
    app: Application,
    request_handler: Type[RequestHandler],
    *simple_route_list: "SimpleRoute",
    prefix: str = "",
    title: str = "",
) -> None:

    rule_list: _RuleList = []
    for simple_route in simple_route_list:
        add_route_plugin(simple_route, SimpleRoutePlugin)

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
