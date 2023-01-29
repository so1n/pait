from typing import Any, Optional, Type

from flask import Flask
from werkzeug.exceptions import NotFound

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import OpenAPI
from pait.app.flask._simple_route import SimpleRoute, add_multi_simple_route

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Flask]):
    not_found_exc: Exception = NotFound()
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Flask) -> Any:
        add_multi_simple_route(
            app,
            SimpleRoute(
                url="/<path:route_path>",
                route=self._get_doc_route(),
                methods=["GET"],
            ),
            SimpleRoute(url="/openapi.json", route=self._get_openapi_route(app), methods=["GET"]),
            prefix=self.prefix,
            title=self.title,
            import_name=__name__,
        )


def add_doc_route(
    app: Flask,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    openapi: Optional[Type["OpenAPI"]] = None,
    project_name: str = "",
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        project_name=project_name,
        app=app,
        openapi=openapi,
    )
