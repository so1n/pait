import json
import logging
from typing import Any, Dict, List, Optional

from sanic import response
from sanic.app import Sanic
from sanic.blueprints import Blueprint
from sanic.exceptions import NotFound
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.field import Depends, Query
from pait.g import config
from pait.model.core import PaitCoreModel

from ._load_app import load_app
from ._pait import pait

__all__ = ["add_doc_route"]


def add_doc_route(
    app: Sanic,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if pin_code:
        logging.info(f"doc route start pin code:{pin_code}")

    def _get_request_pin_code(r_pin_code: str = Query.i("", alias="pin_code")) -> Optional[str]:
        if pin_code:
            if r_pin_code != pin_code:
                raise NotFound
        return r_pin_code

    def _get_open_json_url(request: Request, r_pin_code: str) -> str:
        openapi_json_url: str = (
            f"{request.scheme}://{request.host}{'/'.join(request.path.split('/')[:-1])}/openapi.json"
        )
        if r_pin_code:
            openapi_json_url += f"?pin_code={r_pin_code}"
        return openapi_json_url

    @pait()
    def get_redoc_html(request: Request, r_pin_code: str = Depends.i(_get_request_pin_code)) -> HTTPResponse:
        return response.html(_get_redoc_html(_get_open_json_url(request, r_pin_code), title))

    @pait()
    def get_swagger_ui_html(request: Request, r_pin_code: str = Depends.i(_get_request_pin_code)) -> HTTPResponse:
        return response.html(_get_swagger_ui_html(_get_open_json_url(request, r_pin_code), title))

    @pait(pre_depend_list=[_get_request_pin_code])
    def openapi_route(request: Request) -> HTTPResponse:
        pait_dict: Dict[str, PaitCoreModel] = load_app(request.app)
        pait_openapi: PaitOpenApi = PaitOpenApi(
            pait_dict,
            title=title,
            open_api_server_list=[{"url": f"{request.scheme}://{request.host}", "description": ""}],
            open_api_tag_list=open_api_tag_list,
        )
        return response.json(pait_openapi.open_api_dict, dumps=json.dumps, cls=config.json_encoder)

    blueprint: Blueprint = Blueprint("api doc", prefix)
    blueprint.add_route(get_redoc_html, "/redoc", methods={"GET"})
    blueprint.add_route(get_swagger_ui_html, "/swagger", methods={"GET"})
    blueprint.add_route(openapi_route, "/openapi.json", methods={"GET"})
    app.blueprint(blueprint)
