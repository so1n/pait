from abc import ABC
from typing import Any, Dict, List, Optional

from tornado.web import Application, RequestHandler

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

__all__ = ["add_doc_route"]


def add_doc_route(
    app: Application,
    scheme: Optional[str] = None,
    open_json_url_only_path: bool = False,
    prefix: str = "/",
    pin_code: str = "",
    title: str = "Pait Doc",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
) -> None:

    doc_pait: Pait = Pait(
        author=config.author or ("so1n",),
        status=config.status or PaitStatus.release,
        tag=(Tag("pait_doc", desc="pait default doc route"),),
        group="pait_doc",
    )

    class NotFound(Exception):
        pass

    def _get_request_pin_code(r_pin_code: str = Query.i("", alias="pin_code")) -> Optional[str]:
        if pin_code:
            if r_pin_code != pin_code:
                raise NotFound
        return r_pin_code

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

        def _get_open_json_url(self, r_pin_code: str) -> str:
            _scheme: str = scheme or self.request.protocol
            if open_json_url_only_path:
                openapi_json_url: str = f"{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
            else:
                openapi_json_url = (
                    f"{_scheme}://{self.request.host}{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
                )
            if r_pin_code:
                openapi_json_url += f"?pin_code={r_pin_code}"
            return openapi_json_url

    class GetRedocHtmlHandle(BaseHandle, ABC):
        @doc_pait()
        async def get(self, r_pin_code: str = Depends.i(_get_request_pin_code)) -> None:
            self.write(_get_redoc_html(self._get_open_json_url(r_pin_code), title))

    class GetSwaggerUiHtmlHandle(BaseHandle, ABC):
        @doc_pait()
        async def get(self, r_pin_code: str = Depends.i(_get_request_pin_code)) -> None:
            self.write(_get_swagger_ui_html(self._get_open_json_url(r_pin_code), title))

    class OpenApiHandle(BaseHandle, ABC):
        @doc_pait(pre_depend_list=[_get_request_pin_code])
        async def get(self) -> None:
            pait_dict: Dict[str, PaitCoreModel] = load_app(self.application)
            _scheme: str = scheme or self.request.protocol
            pait_openapi: PaitOpenApi = PaitOpenApi(
                pait_dict,
                title=title,
                open_api_server_list=[{"url": f"{_scheme}://{self.request.host}", "description": ""}],
                open_api_tag_list=open_api_tag_list,
            )
            self.write(pait_openapi.open_api_dict)

    if not prefix.endswith("/"):
        prefix = prefix + "/"
    # Method 1
    # app.add_handlers(
    #     r".*$",
    #     [
    #         (r"{}redoc".format(prefix), GetRedocHtmlHandle),
    #         (r"{}swagger".format(prefix), GetSwaggerUiHtmlHandle),
    #         (r"{}openapi.json".format(prefix), OpenApiHandle),
    #     ]
    # )
    #
    # Method 2
    # app.add_handlers(
    # app.default_router.add_rules(
    #     [
    #         (r"{}redoc".format(prefix), GetRedocHtmlHandle),
    #         (r"{}swagger".format(prefix), GetSwaggerUiHtmlHandle),
    #         (r"{}openapi.json".format(prefix), OpenApiHandle),
    #     ]
    # )
    #
    # Method 3
    app.wildcard_router.add_rules(
        [
            (r"{}redoc".format(prefix), GetRedocHtmlHandle),
            (r"{}swagger".format(prefix), GetSwaggerUiHtmlHandle),
            (r"{}openapi.json".format(prefix), OpenApiHandle),
        ]
    )
    from tornado.web import AnyMatches, Rule, _ApplicationRouter

    app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])
