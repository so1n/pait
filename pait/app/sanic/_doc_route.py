import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from sanic import response
from sanic.app import Sanic
from sanic.blueprints import Blueprint
from sanic.exceptions import NotFound
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenAPI
from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import DocHtmlRespModel, OpenAPIRespModel
from pait.field import Depends
from pait.g import config
from pait.model.core import PaitCoreModel
from pait.model.template import TemplateContext

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Sanic]):
    not_found_exc: Exception = NotFound("")

    def _gen_route(self, app: Sanic) -> Any:
        doc_pait = self._get_doc_pait(Pait)

        def _get_open_json_url(request: Request, r_pin_code: str, url_dict: Dict[str, Any]) -> str:
            _scheme: str = self.scheme or request.scheme
            if self.open_json_url_only_path:
                openapi_json_url: str = f"{'/'.join(request.path.split('/')[:-1])}/openapi.json"
            else:
                openapi_json_url = f"{_scheme}://{request.host}{'/'.join(request.path.split('/')[:-1])}/openapi.json"
            if r_pin_code:
                url_dict["pin_code"] = r_pin_code
            openapi_json_url += "?" + urlencode(url_dict)
            return openapi_json_url

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_redoc_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTTPResponse:
            return response.html(
                _get_redoc_html(
                    _get_open_json_url(request, r_pin_code, url_dict),
                    src_url=self.redoc_src_url,
                    title=self.title,
                )
            )

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_swagger_ui_html(
            request: Request,
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> HTTPResponse:
            return response.html(
                _get_swagger_ui_html(
                    _get_open_json_url(request, r_pin_code, url_dict),
                    title=self.title,
                    swagger_ui_bundle=self.swagger_ui_bundle,
                    swagger_ui_standalone_preset=self.swagger_ui_standalone_preset,
                    swagger_ui_url=self.swagger_ui_url,
                )
            )

        @doc_pait(pre_depend_list=[self._get_request_pin_code], response_model_list=[OpenAPIRespModel])
        def openapi_route(
            request: Request, url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map(extra_key=True))
        ) -> HTTPResponse:
            pait_dict: Dict[str, PaitCoreModel] = load_app(request.app, project_name=self.project_name)
            _scheme: str = self.scheme or request.scheme
            with TemplateContext(url_dict):
                pait_openapi: PaitOpenAPI = PaitOpenAPI(
                    pait_dict,
                    title=self.title,
                    open_api_server_list=[{"url": f"{_scheme}://{request.host}", "description": ""}],
                    open_api_tag_list=self.open_api_tag_list,
                )
                return response.json(pait_openapi.open_api_dict, dumps=json.dumps, cls=config.json_encoder)

        blueprint: Blueprint = Blueprint(self.title, self.prefix)
        blueprint.add_route(get_redoc_html, "/redoc", methods={"GET"})
        blueprint.add_route(get_swagger_ui_html, "/swagger", methods={"GET"})
        blueprint.add_route(openapi_route, "/openapi.json", methods={"GET"})
        app.blueprint(blueprint)


def add_doc_route(
    app: Sanic,
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
