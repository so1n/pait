from typing import Any, Optional, Type

from flask import Blueprint, Flask, Response, jsonify
from werkzeug.exceptions import NotFound

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import OpenAPI

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Flask, Response]):
    not_found_exc: Exception = NotFound()
    html_response = staticmethod(lambda resp: resp)
    json_response = staticmethod(jsonify)
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Flask) -> Any:
        blueprint: Blueprint = Blueprint(self.title, __name__, url_prefix=self.prefix)
        blueprint.add_url_rule("/<path:route_path>", "doc ui route", view_func=self._get_doc_route(), methods=["GET"])
        blueprint.add_url_rule("/openapi.json", view_func=self._get_openapi_route(app), methods=["GET"])
        app.register_blueprint(blueprint)


def add_doc_route(
    app: Flask,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    openapi: Optional[Type[OpenAPI]] = None,
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
