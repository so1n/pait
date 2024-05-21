from typing import Any, Callable, Optional

from starlette.applications import Starlette

from pait.app.base.api_route import BaseAPIRoute, Type
from pait.model.core import get_core_model

from ._load_app import get_openapi_path
from ._pait import Pait


def default_replace_openapi_url_to_url(url: str) -> str:
    return url


class APIRoute(BaseAPIRoute):
    @property
    def _pait_type(self) -> Type[Pait]:
        return Pait

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        return get_openapi_path(path_str)

    def inject(
        self, app: Starlette, replace_openapi_url_to_url: Optional[Callable[[str], str]] = None, **kwargs: Any
    ) -> None:
        if not replace_openapi_url_to_url:
            replace_openapi_url_to_url = default_replace_openapi_url_to_url

        for route_dc in self.route:
            route = self._pait(**route_dc.pait_param)(route_dc.route)
            get_core_model(route).openapi_path = self.get_openapi_path(route_dc.path)
            _framework_extra_param = self.framework_extra_param.copy()
            _framework_extra_param.update(route_dc.framework_extra_param)
            app.add_route(
                replace_openapi_url_to_url(route_dc.path), route, methods=route_dc.method_list, **_framework_extra_param
            )
