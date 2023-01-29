from typing import Any, Dict, Optional, Set, Type

from starlette.applications import Starlette
from starlette.exceptions import HTTPException

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import OpenAPI
from pait.app.starlette._simple_route import SimpleRoute, add_multi_simple_route

from ._load_app import load_app
from ._pait import Pait

__all__ = ["AddDocRoute", "add_doc_route"]
prefix_set_dict: Dict[Starlette, Set[str]] = {}


class AddDocRoute(_AddDocRoute[Starlette]):
    not_found_exc: Exception = HTTPException(
        status_code=404,
        detail=(
            "The requested URL was not found on the server. If you entered"
            " the URL manually please check your spelling and try again."
        ),
    )
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Starlette) -> Any:
        add_multi_simple_route(
            app,
            SimpleRoute(url="/openapi.json", route=self._get_openapi_route(app), methods=["GET"]),
            SimpleRoute(url="/{route_path}", route=self._get_doc_route(), methods=["GET"]),
            prefix=self.prefix,
            title=self.title,
        )


def add_doc_route(
    app: Starlette,
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
        openapi=openapi,
        project_name=project_name,
        app=app,
    )
