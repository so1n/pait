import logging
from typing import Any, Dict, List, Optional

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.field import Depends, Query
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag

from ._load_app import load_app
from ._pait import Pait


def add_doc_route(
    app: Starlette,
    scheme: Optional[str] = None,
    open_json_url_only_path: bool = False,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if pin_code:
        logging.info(f"doc route start pin code:{pin_code}")

    doc_pait: Pait = Pait(
        author=config.author or ("so1n",),
        status=config.status or PaitStatus.release,
        tag=(Tag("pait_doc", desc="pait default doc route"),),
        group="pait_doc",
    )

    def _get_request_pin_code(r_pin_code: str = Query.i("", alias="pin_code")) -> Optional[str]:
        if pin_code:
            if r_pin_code != pin_code:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "The requested URL was not found on the server. If you entered"
                        " the URL manually please check your spelling and try again."
                    ),
                )
        return r_pin_code

    def _get_open_json_url(request: Request, r_pin_code: str) -> str:
        _scheme: str = scheme or request.url.scheme
        if open_json_url_only_path:
            openapi_json_url: str = f"{'/'.join(request.url.path.split('/')[:-1])}/openapi.json"
        else:
            url: str = f"{_scheme}://{request.url.hostname}"
            if request.url.port:
                url += f":{request.url.port}"  # pragma: no cover
            openapi_json_url = f"{url}{'/'.join(request.url.path.split('/')[:-1])}/openapi.json"
        if r_pin_code:
            openapi_json_url += f"?pin_code={r_pin_code}"
        return openapi_json_url

    @doc_pait()
    def get_redoc_html(request: Request, r_pin_code: str = Depends.i(_get_request_pin_code)) -> HTMLResponse:
        return HTMLResponse(_get_redoc_html(_get_open_json_url(request, r_pin_code), title))

    @doc_pait()
    def get_swagger_ui_html(request: Request, r_pin_code: str = Depends.i(_get_request_pin_code)) -> HTMLResponse:
        return HTMLResponse(_get_swagger_ui_html(_get_open_json_url(request, r_pin_code), title))

    @doc_pait(pre_depend_list=[_get_request_pin_code])
    def openapi_route(request: Request) -> JSONResponse:
        pait_dict: Dict[str, PaitCoreModel] = load_app(request.app)
        _scheme: str = scheme or request.url.scheme
        url: str = f"{_scheme}://{request.url.hostname}"
        if request.url.port:
            url += f":{request.url.port}"  # pragma: no cover
        pait_openapi: PaitOpenApi = PaitOpenApi(
            pait_dict,
            title=title,
            open_api_server_list=[{"url": url, "description": ""}],
            open_api_tag_list=open_api_tag_list,
        )
        return JSONResponse(pait_openapi.open_api_dict)

    route: Mount = Mount(
        prefix,
        name="api doc",
        routes=[
            Route("/redoc", get_redoc_html, methods=["GET"]),
            Route("/swagger", get_swagger_ui_html, methods=["GET"]),
            Route("/openapi.json", openapi_route, methods=["GET"]),
        ],
    )
    app.routes.append(route)
