from typing import Any, Dict, List, Optional, Set

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute

from ._load_app import load_app
from ._pait import Pait

__all__ = ["AddDocRoute", "add_doc_route"]
prefix_set_dict: Dict[Starlette, Set[str]] = {}


class AddDocRoute(_AddDocRoute[Starlette, Response]):
    not_found_exc: Exception = HTTPException(
        status_code=404,
        detail=(
            "The requested URL was not found on the server. If you entered"
            " the URL manually please check your spelling and try again."
        ),
    )
    html_response = HTMLResponse
    json_response = JSONResponse
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Starlette) -> Any:
        # prefix `/` route group must be behind other route group
        if app not in prefix_set_dict:
            prefix_set: Set[str] = set()
            prefix_set_dict[app] = prefix_set
        else:
            prefix_set = prefix_set_dict[app]
        for prefix in prefix_set:
            if self.prefix.startswith(prefix):
                raise RuntimeError(f"prefix:{prefix} already exists, can use:{self.prefix}")

        prefix_set.add(self.prefix)

        route: Mount = Mount(
            self.prefix,
            name=self.title,
            routes=[
                Route("/openapi.json", self._get_openapi_route(app), methods=["GET"]),
                Route("/{route_path}", self._get_doc_route(), methods=["GET"]),
            ],
        )
        app.routes.append(route)


def add_doc_route(
    app: Starlette,
    scheme: Optional[str] = None,
    open_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
    project_name: str = "",
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=open_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        open_api_tag_list=open_api_tag_list,
        project_name=project_name,
        app=app,
    )
