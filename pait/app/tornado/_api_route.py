from typing import Any, Callable, Optional, Type

from tornado.routing import AnyMatches, Rule
from tornado.web import Application, RequestHandler, _ApplicationRouter

from pait.app.base.api_route import BaseAPIRoute, CbcRouteDc, RouteDc
from pait.model.core import get_core_model

from ._load_app import get_openapi_path
from ._pait import Pait
from ._simple_route import default_replace_openapi_url_to_url


class APIRoute(BaseAPIRoute):

    @property
    def _pait_type(self) -> Type[Pait]:
        return Pait

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        return get_openapi_path(path_str)

    def inject(
        self,
        app: Application,
        replace_openapi_url_to_url: Optional[Callable[[str], str]] = None,
        request_handler: Type[RequestHandler] = RequestHandler,
        **kwargs: Any,
    ) -> None:
        rule_list = []
        replace_openapi_url_to_url = replace_openapi_url_to_url or default_replace_openapi_url_to_url

        _pait = self._pait_type()
        for route_dc in self.route:
            _framework_extra_param = self.framework_extra_param.copy()
            _framework_extra_param.update(route_dc.framework_extra_param)
            if isinstance(route_dc, RouteDc):
                if "request_handler" in _framework_extra_param:
                    request_handler = _framework_extra_param.pop("request_handler")
                route = _pait(**route_dc.pait_param)(route_dc.route)
                get_core_model(route).openapi_path = self.get_openapi_path(route_dc.path)
                route_title = _framework_extra_param.pop("route_title", route.__name__.title() + "Handler")
                route_model = _framework_extra_param.pop("route_model", f"{__name__}.{route.__name__}")
                route_class = type(route_title, (request_handler,), {"__model__": route_model})

                for method in route_dc.method_list:
                    setattr(route_class, method.lower(), route)
                    rule_list.append((replace_openapi_url_to_url(route_dc.path), route_class))
            elif isinstance(route_dc, CbcRouteDc) and issubclass(route_dc.route, RequestHandler):
                self._cbv_handler(_pait, route_dc.route, route_dc.pait_param)
                rule_list.append((replace_openapi_url_to_url(route_dc.path), route_dc.route))
            else:
                raise ValueError(f"route_dc type error: {route_dc}")

        app.wildcard_router.add_rules(rule_list)
        app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])
