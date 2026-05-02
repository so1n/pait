from typing import Any, Dict

from sanic import Sanic

from pait.app.base.api_route import BaseAPIRoute, CbvRouteDc, RouteDc, Type
from pait.types import CallType

from ._app_helper import cbv_type_tuple
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

    def _is_cbv_route(self, route: Type) -> bool:
        return issubclass(route, cbv_type_tuple)

    def _add_api_route(
        self,
        app: Sanic,
        route: CallType,
        route_dc: RouteDc,
        url: str,
        framework_extra_param: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        app.add_route(route, url, methods=set(route_dc.method_list), **framework_extra_param)

    def _add_cbv_route(
        self, app: Sanic, route_dc: CbvRouteDc, url: str, framework_extra_param: Dict[str, Any], **kwargs: Any
    ) -> None:
        app.add_route(route_dc.route.as_view(), url, **framework_extra_param)
