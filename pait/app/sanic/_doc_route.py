from typing import Any, Dict, List, Optional

from sanic import response
from sanic.app import Sanic
from sanic.blueprints import Blueprint
from sanic.exceptions import NotFound
from sanic.response import HTTPResponse
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Sanic, HTTPResponse]):
    not_found_exc: Exception = NotFound("")
    html_response = staticmethod(response.html)
    json_response = staticmethod(response.json)
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Sanic) -> Any:
        blueprint: Blueprint = Blueprint(self.title, self.prefix)
        blueprint.add_route(self._get_doc_route(), "/<route_path>", methods={"GET"})
        blueprint.add_route(self._get_openapi_route(app), "/openapi.json", methods={"GET"})
        app.blueprint(blueprint)


def add_doc_route(
    app: Sanic,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
    project_name: str = "",
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        open_api_tag_list=open_api_tag_list,
        project_name=project_name,
        app=app,
    )
