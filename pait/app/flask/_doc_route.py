from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from flask import Blueprint, Flask, Response, current_app, make_response, request
from werkzeug.exceptions import NotFound

from pait.api_doc.open_api import PaitOpenAPI
from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import DocHtmlRespModel, OpenAPIRespModel
from pait.field import Depends
from pait.model.core import PaitCoreModel
from pait.model.template import TemplateContext

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class AddDocRoute(_AddDocRoute[Flask]):
    not_found_exc: Exception = NotFound()

    def _gen_route(self, app: Flask) -> Any:
        doc_pait = self._get_doc_pait(Pait)

        def _get_open_json_url(r_pin_code: str, url_dict: Dict[str, Any]) -> str:
            _scheme: str = self.scheme or request.scheme
            request_path: str = "/".join(request.path.split("/")[:-1])
            if self.open_json_url_only_path:
                openapi_json_url: str = f"{request_path}/openapi.json"
            else:
                openapi_json_url = f"{_scheme}://{request.host}{request_path}/openapi.json"
            if r_pin_code:
                url_dict["pin_code"] = r_pin_code
            openapi_json_url += "?" + urlencode(url_dict)
            return openapi_json_url

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_redoc_html(
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> str:
            return self._get_redoc_html(_get_open_json_url(r_pin_code, url_dict))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_rapi_doc_html(
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> str:
            return self._get_rapidoc_html(_get_open_json_url(r_pin_code, url_dict))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_rapi_pdf_html(
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> str:
            return self._get_rapipdf_html(_get_open_json_url(r_pin_code, url_dict))

        @doc_pait(response_model_list=[DocHtmlRespModel])
        def get_swagger_ui_html(
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> str:
            return self._get_swagger_ui_html(_get_open_json_url(r_pin_code, url_dict))

        @doc_pait(pre_depend_list=[self._get_request_pin_code], response_model_list=[OpenAPIRespModel])
        def openapi_route(
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map(extra_key=True))
        ) -> Response:
            _scheme: str = self.scheme or request.scheme
            pait_dict: Dict[str, PaitCoreModel] = load_app(current_app, project_name=self.project_name)
            with TemplateContext(url_dict):
                pait_openapi: PaitOpenAPI = PaitOpenAPI(
                    pait_dict,
                    title=self.title,
                    open_api_server_list=[{"url": f"{_scheme}://{request.host}", "description": ""}],
                    open_api_tag_list=self.open_api_tag_list,
                )
                response: Response = make_response(pait_openapi.content)
                response.mimetype = "application/json"
            return response

        blueprint: Blueprint = Blueprint(self.title, __name__, url_prefix=self.prefix)
        blueprint.add_url_rule("/redoc", view_func=get_redoc_html, methods=["GET"])
        blueprint.add_url_rule("/swagger", view_func=get_swagger_ui_html, methods=["GET"])
        blueprint.add_url_rule("/rapidoc", view_func=get_rapi_doc_html, methods=["GET"])
        blueprint.add_url_rule("/rapipdf", view_func=get_rapi_pdf_html, methods=["GET"])
        blueprint.add_url_rule("/openapi.json", view_func=openapi_route, methods=["GET"])
        app.register_blueprint(blueprint)


def add_doc_route(
    app: Flask,
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
