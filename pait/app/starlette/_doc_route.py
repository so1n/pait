from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlencode

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import Mount, Route

from pait.api_doc.open_api import PaitOpenAPI
from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import DocHtmlRespModel, OpenAPIRespModel
from pait.field import Depends
from pait.model.core import PaitCoreModel
from pait.model.template import TemplateContext

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
        doc_pait = self._get_doc_pait(Pait)

        def _get_open_json_url(request: Request, r_pin_code: str, url_dict: Dict[str, Any]) -> str:
            _scheme: str = self.scheme or request.url.scheme
            request_path: str = "/".join(request.url.path.split("/")[:-1])
            if self.open_json_url_only_path:
                openapi_json_url: str = f"{request_path}/openapi.json"
            else:
                url: str = f"{_scheme}://{request.url.hostname}"
                if request.url.port:
                    url += f":{request.url.port}"  # pragma: no cover
                openapi_json_url = f"{url}{request_path}/openapi.json"
            if r_pin_code:
                url_dict["pin_code"] = r_pin_code
            openapi_json_url += "?" + urlencode(url_dict)
            return openapi_json_url

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_redoc_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTMLResponse:
            return HTMLResponse(self._get_redoc_html(_get_open_json_url(request, r_pin_code, url_dict)))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_rapi_doc_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTMLResponse:
            return HTMLResponse(self._get_rapidoc_html(_get_open_json_url(request, r_pin_code, url_dict)))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_rapi_pdf_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTMLResponse:
            return HTMLResponse(self._get_rapipdf_html(_get_open_json_url(request, r_pin_code, url_dict)))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_swagger_ui_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTMLResponse:
            return HTMLResponse(self._get_swagger_ui_html(_get_open_json_url(request, r_pin_code, url_dict)))

        @doc_pait(pre_depend_list=[self._get_request_pin_code], response_model_list=[OpenAPIRespModel])
        def openapi_route(
            request: Request, url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map(extra_key=True))
        ) -> Response:
            pait_dict: Dict[str, PaitCoreModel] = load_app(request.app, project_name=self.project_name)
            _scheme: str = self.scheme or request.url.scheme
            url: str = f"{_scheme}://{request.url.hostname}"
            if request.url.port:
                url += f":{request.url.port}"  # pragma: no cover
            with TemplateContext(url_dict):
                pait_openapi: PaitOpenAPI = PaitOpenAPI(
                    pait_dict,
                    title=self.title,
                    open_api_server_list=[{"url": url, "description": ""}],
                    open_api_tag_list=self.open_api_tag_list,
                )
                return Response(pait_openapi.content, media_type="application/json")

        route: Mount = Mount(
            self.prefix,
            name=self.title,
            routes=[
                Route("/redoc", get_redoc_html, methods=["GET"]),
                Route("/swagger", get_swagger_ui_html, methods=["GET"]),
                Route("/rapidoc", get_rapi_doc_html, methods=["GET"]),
                Route("/rapipdf", get_rapi_pdf_html, methods=["GET"]),
                Route("/openapi.json", openapi_route, methods=["GET"]),
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
        open_json_url_only_path=open_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        open_api_tag_list=open_api_tag_list,
        project_name=project_name,
        app=app,
    )
