from typing import Any, Dict, MutableSequence

from django.urls import path
from django.views import View
from django.views.decorators.http import require_http_methods

from pait.app.base.api_route import BaseAPIRoute, CbvRouteDc, RouteDc, Type
from pait.types import CallType

from ._load_app import get_openapi_path
from ._pait import Pait
from ._path import path_converter


class APIRoute(BaseAPIRoute):
    replace_openapi_url_to_url = staticmethod(path_converter.replace_openapi_url_to_url)  # type: ignore[arg-type]

    @property
    def _pait_type(self) -> Type[Pait]:
        return Pait

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        return get_openapi_path(path_str)

    def _is_cbv_route(self, route: Type) -> bool:
        return issubclass(route, View)

    def _add_api_route(
        self,
        app: MutableSequence,
        route: CallType,
        route_dc: RouteDc,
        url: str,
        framework_extra_param: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        method_set = {method.upper() for method in route_dc.method_list}
        route = require_http_methods(list(method_set))(route)
        setattr(route, "_pait_method_set", method_set)
        app.append(path(url.lstrip("/"), route, **framework_extra_param))

    def _add_cbv_route(
        self, app: MutableSequence, route_dc: CbvRouteDc, url: str, framework_extra_param: Dict[str, Any], **kwargs: Any
    ) -> None:
        app.append(path(url.lstrip("/"), route_dc.route.as_view(), **framework_extra_param))
