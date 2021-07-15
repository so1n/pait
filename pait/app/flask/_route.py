import logging
from typing import Any, Dict, List, Optional

from flask import Blueprint, Flask, current_app, request
from werkzeug.exceptions import NotFound

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.model.core import PaitCoreModel

from ._load_app import load_app

__all__ = ["add_doc_route"]


def add_doc_route(
    app: Flask,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    if pin_code:
        logging.info(f"doc route start pin code:{pin_code}")

    def _get_request_pin_code() -> Optional[str]:
        r_pin_code: Optional[str] = request.args.to_dict().get("pin_code", None)
        if pin_code:
            if r_pin_code != pin_code:
                raise NotFound
        return r_pin_code

    def _get_open_json_url() -> str:
        r_pin_code: Optional[str] = _get_request_pin_code()
        openapi_json_url: str = f"http://{request.host}{'/'.join(request.path.split('/')[:-1])}/openapi.json"
        if r_pin_code:
            openapi_json_url += f"?pin_code={r_pin_code}"
        return openapi_json_url

    def get_redoc_html() -> str:
        return _get_redoc_html(_get_open_json_url(), title)

    def get_swagger_ui_html() -> str:
        return _get_swagger_ui_html(_get_open_json_url(), title)

    def openapi_route() -> dict:
        _get_request_pin_code()
        pait_dict: Dict[str, PaitCoreModel] = load_app(current_app)
        pait_openapi: PaitOpenApi = PaitOpenApi(
            pait_dict,
            title=title,
            open_api_server_list=[{"url": f"http://{request.host}", "description": ""}],
            open_api_tag_list=open_api_tag_list,
        )
        return pait_openapi.open_api_dict

    blueprint: Blueprint = Blueprint("api doc", __name__, url_prefix=prefix)
    blueprint.add_url_rule("/redoc", view_func=get_redoc_html, methods=["GET"])
    blueprint.add_url_rule("/swagger", view_func=get_swagger_ui_html, methods=["GET"])
    blueprint.add_url_rule("/openapi.json", view_func=openapi_route, methods=["GET"])
    app.register_blueprint(blueprint)
