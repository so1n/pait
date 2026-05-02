from typing import Any, Dict, List, Tuple, Type

from tornado.routing import AnyMatches, Rule
from tornado.web import Application, RequestHandler, _ApplicationRouter

from pait.app.base.api_route import BaseAPIRoute, CbvRouteDc, RouteDc
from pait.types import CallType

from ._load_app import get_openapi_path
from ._pait import Pait
from ._simple_route import default_replace_openapi_url_to_url


class APIRoute(BaseAPIRoute):
    replace_openapi_url_to_url = staticmethod(default_replace_openapi_url_to_url)  # type: ignore[arg-type]

    @property
    def _pait_type(self) -> Type[Pait]:
        return Pait

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        return get_openapi_path(path_str)

    def _before_inject(
        self, app: Application, request_handler: Type[RequestHandler] = RequestHandler, **kwargs: Any
    ) -> None:
        self._rule_list: List[Tuple[str, Type[RequestHandler]]] = []
        self._request_handler: Type[RequestHandler] = request_handler
        self._route_class_dict: Dict[Tuple[str, Type[RequestHandler]], Type[RequestHandler]] = {}

    def _is_cbv_route(self, route: Type) -> bool:
        return issubclass(route, RequestHandler)

    def _add_api_route(
        self,
        app: Application,
        route: CallType,
        route_dc: RouteDc,
        url: str,
        framework_extra_param: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        route_name = route.__name__  # type: ignore[union-attr]
        request_handler = framework_extra_param.pop("request_handler", self._request_handler)
        route_title = framework_extra_param.pop("route_title", route_name.title() + "Handler")
        route_model = framework_extra_param.pop("route_model", f"{__name__}.{route_name}")
        route_class_key = (url, request_handler)
        route_class = self._route_class_dict.get(route_class_key)
        if route_class is None:
            route_class = type(route_title, (request_handler,), {"__model__": route_model})
            self._route_class_dict[route_class_key] = route_class
            self._rule_list.append((url, route_class))

        for method in route_dc.method_list:
            setattr(route_class, method.lower(), route)

    def _add_cbv_route(
        self, app: Application, route_dc: CbvRouteDc, url: str, framework_extra_param: Dict[str, Any], **kwargs: Any
    ) -> None:
        self._rule_list.append((url, route_dc.route))

    def _after_inject(self, app: Application, **kwargs: Any) -> None:
        app.wildcard_router.add_rules(self._rule_list)  # type: ignore
        app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])
