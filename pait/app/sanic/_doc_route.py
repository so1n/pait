from typing import Any, Optional, Type

from sanic.app import Sanic
from sanic.exceptions import NotFound
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import OpenAPI
from pait.app.sanic._simple_route import SimpleRoute, add_multi_simple_route

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Sanic]):
    not_found_exc: Exception = NotFound("")
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Sanic) -> Any:
        add_multi_simple_route(
            app,
            SimpleRoute(url="/<route_path>", route=self._get_doc_route(), methods=["GET"]),
            SimpleRoute(url="/openapi.json", route=self._get_openapi_route(app), methods=["GET"]),
            prefix=self.prefix,
            title=self.title,
        )


def add_doc_route(
    app: Sanic,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    openapi: Optional[Type["OpenAPI"]] = None,
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        openapi=openapi,
        app=app,
    )
