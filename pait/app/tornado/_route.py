from abc import ABC
from typing import Any, Dict, List, Optional

from tornado.web import Application, RequestHandler

from pait.api_doc.html import get_redoc_html as _get_redoc_html
from pait.api_doc.html import get_swagger_ui_html as _get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenApi
from pait.model.core import PaitCoreModel

from ._load_app import load_app

__all__ = ["add_doc_route"]


def add_doc_route(
    app: Application,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:
    class NotFound(Exception):
        pass

    class BaseHandle(RequestHandler, ABC):
        def _handle_request_exception(self, exc: BaseException) -> None:
            self.set_status(404)
            self.write(
                (
                    "The requested URL was not found on the server. If you entered"
                    " the URL manually please check your spelling and try again."
                )
            )
            self.finish()

        def _get_request_pin_code(self) -> Optional[str]:
            r_pin_code: Optional[str] = {
                key: value[0].decode() for key, value in self.request.query_arguments.items()
            }.get("pin_code", None)
            if pin_code:
                if r_pin_code != pin_code:
                    raise NotFound
            return r_pin_code

        def _get_open_json_url(self) -> str:
            r_pin_code: Optional[str] = self._get_request_pin_code()
            openapi_json_url: str = (
                f"http://{self.request.host}{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
            )
            if r_pin_code:
                openapi_json_url += f"?pin_code={r_pin_code}"
            return openapi_json_url

    class GetRedocHtmlHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self.write(_get_redoc_html(self._get_open_json_url(), title))

    class GetSwaggerUiHtmlHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self.write(_get_swagger_ui_html(self._get_open_json_url(), title))

    class OpenApiHandle(BaseHandle, ABC):
        async def get(self) -> None:
            self._get_request_pin_code()
            pait_dict: Dict[str, PaitCoreModel] = load_app(self.application)
            pait_openapi: PaitOpenApi = PaitOpenApi(
                pait_dict,
                title=title,
                open_api_server_list=[{"url": f"http://{self.request.host}", "description": ""}],
                open_api_tag_list=open_api_tag_list,
            )
            self.write(pait_openapi.open_api_dict)

    if not prefix.endswith("/"):
        prefix = prefix + "/"
    app.add_handlers(
        r".*",
        [
            (r"{}redoc".format(prefix), GetRedocHtmlHandle),
            (r"{}swagger".format(prefix), GetSwaggerUiHtmlHandle),
            (r"{}openapi.json".format(prefix), OpenApiHandle),
        ],
    )
