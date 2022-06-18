from abc import ABC
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from tornado.web import Application, RequestHandler

from pait.api_doc.open_api import PaitOpenAPI
from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.field import Depends
from pait.model.core import PaitCoreModel
from pait.model.template import TemplateContext

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class NotFound(Exception):
    pass


class AddDocRoute(_AddDocRoute[Application]):
    not_found_exc: Exception = NotFound()

    def _gen_route(self, app: Application) -> Any:
        doc_pait = self._get_doc_pait(Pait)
        doc_route_self: "AddDocRoute" = self

        class BaseHandle(RequestHandler, ABC):
            def _handle_request_exception(self, exc: BaseException) -> None:
                if isinstance(exc, NotFound):
                    self.set_status(404)
                    self.write(
                        (
                            "The requested URL was not found on the server. If you entered"
                            " the URL manually please check your spelling and try again."
                        )
                    )
                    self.finish()
                else:
                    self.set_status(500)  # pragma: no cover
                    self.finish()  # pragma: no cover

            def _get_open_json_url(self, r_pin_code: str, url_dict: Dict[str, Any]) -> str:
                _scheme: str = doc_route_self.scheme or self.request.protocol
                if doc_route_self.open_json_url_only_path:
                    openapi_json_url: str = f"{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
                else:
                    openapi_json_url = (
                        f"{_scheme}://{self.request.host}{'/'.join(self.request.path.split('/')[:-1])}/openapi.json"
                    )
                if r_pin_code:
                    url_dict["pin_code"] = r_pin_code
                openapi_json_url += "?" + urlencode(url_dict)
                return openapi_json_url

        class GetRedocHtmlHandle(BaseHandle, ABC):
            @doc_pait()
            async def get(
                self,
                r_pin_code: str = Depends.i(doc_route_self._get_request_pin_code),
                url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
            ) -> None:
                self.write(doc_route_self._get_redoc_html(self._get_open_json_url(r_pin_code, url_dict)))

        class GetRapiDocHtmlHandle(BaseHandle, ABC):
            @doc_pait()
            async def get(
                self,
                r_pin_code: str = Depends.i(self._get_request_pin_code),
                url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
            ) -> None:
                self.write(doc_route_self._get_rapidoc_html(self._get_open_json_url(r_pin_code, url_dict)))

        class GetRapiPdfHtmlHandle(BaseHandle, ABC):
            @doc_pait()
            async def get(
                self,
                r_pin_code: str = Depends.i(self._get_request_pin_code),
                url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
            ) -> None:
                self.write(doc_route_self._get_rapipdf_html(self._get_open_json_url(r_pin_code, url_dict)))

        class GetSwaggerUiHtmlHandle(BaseHandle, ABC):
            @doc_pait()
            async def get(
                self,
                r_pin_code: str = Depends.i(doc_route_self._get_request_pin_code),
                url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
            ) -> None:
                self.write(doc_route_self._get_swagger_ui_html(self._get_open_json_url(r_pin_code, url_dict)))

        class OpenApiHandle(BaseHandle, ABC):
            @doc_pait(pre_depend_list=[doc_route_self._get_request_pin_code])
            async def get(
                self, url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map(extra_key=True))
            ) -> None:
                pait_dict: Dict[str, PaitCoreModel] = load_app(
                    self.application, project_name=doc_route_self.project_name
                )
                _scheme: str = doc_route_self.scheme or self.request.protocol
                with TemplateContext(url_dict):
                    pait_openapi: PaitOpenAPI = PaitOpenAPI(
                        pait_dict,
                        title=doc_route_self.title,
                        open_api_server_list=[{"url": f"{_scheme}://{self.request.host}", "description": ""}],
                        open_api_tag_list=doc_route_self.open_api_tag_list,
                    )
                    self.set_header("Content-Type", "application/json; charset=UTF-8")
                    self.write(pait_openapi.content)

        prefix: str = doc_route_self.prefix
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
                (r"{}rapidoc".format(prefix), GetRapiDocHtmlHandle),
                (r"{}rapipdf".format(prefix), GetRapiPdfHtmlHandle),
                (r"{}openapi.json".format(prefix), OpenApiHandle),
            ]
        )
        from tornado.web import AnyMatches, Rule, _ApplicationRouter

        app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])


def add_doc_route(
    app: Application,
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
