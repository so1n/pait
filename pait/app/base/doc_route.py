import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar
from urllib.parse import urlencode

from any_api.openapi import web_ui
from pydantic import BaseModel, Field

from pait.core import Pait, PluginManager
from pait.field import Depends, Path, Query
from pait.g import config, pait_context
from pait.model import HtmlResponseModel, JsonResponseModel, PaitCoreModel, PaitStatus, Tag, TemplateContext
from pait.openapi.openapi import InfoModel, OpenAPI, ServerModel

logger: logging.Logger = logging.getLogger(__name__)
__all__ = [
    "DocHtmlRespModel",
    "OpenAPIRespModel",
    "AddDocRoute",
    "default_doc_fn_dict",
    "OpenAPI",
    "InfoModel",
    "ServerModel",
]


class DocHtmlRespModel(HtmlResponseModel):
    class HeaderModel(BaseModel):
        x_example_type: str = Field(default="html", alias="X-Example-Type")

    header: BaseModel = HeaderModel
    description: str = "doc html response"


class OpenAPIRespModel(JsonResponseModel):
    class OpenAPIResponseModel(BaseModel):
        pass

    description: str = "open api json response"
    # TODO replace to openapi response model
    response_data: dict = {}  # type: ignore


APP_T = TypeVar("APP_T")


default_doc_fn_dict: Dict[str, Callable] = {key.split("_")[1]: getattr(web_ui, key) for key in web_ui.__all__}


class DocEnum(str, Enum):
    pass


class AddDocRoute(Generic[APP_T]):
    not_found_exc: Exception
    pait_class: Type[Pait]
    load_app: staticmethod

    def __init__(
        self,
        app: APP_T,
        scheme: Optional[str] = None,
        openapi_json_url_only_path: bool = False,
        prefix: str = "",
        pin_code: str = "",
        title: str = "",
        doc_fn_dict: Optional[Dict[str, Callable]] = None,
        openapi: Optional[Type[OpenAPI]] = None,
    ):
        """
        :param app: The app instance to which the doc route is bound
        :param scheme: The scheme of the specified url, if the value is empty,
            it will be automatically selected according to the request

            Note: If the deployment is HTTP and the site configured by Nginx is HTTPS,
                then need to force the specified scheme to be HTTPS
        :param openapi_json_url_only_path: If True, openapi json url does not include HTTP scheme, hostname and port
            Example:
                openapi_json_url_only_path=True,  url: `/api/path`
                openapi_json_url_only_path=False, url: `http://127.0.0.1:8080/api/path`
        :param prefix: Doc route path prefix
        :param pin_code: If pin_code is set, the pin code parameter needs to be added when requesting doc route
            Example:
                pin_code: None, url `http://127.0.0.1:8080/api/path`
                pin_code: 6666, url `http://127.0.0.1:8080/api/path?pin-code=6666`
        :param title: Doc route group name,
            the title of multiple doc routes registered for the same app instance must be different
        :param openapi: OpenAPI class
        :param doc_fn_dict: doc ui dict, default `pait.app.base.doc_route.default_doc_fn_dict`
        """
        if pin_code:
            logging.info(f"doc route start pin code:{pin_code}")
        self.scheme: Optional[str] = scheme
        self.openapi_json_url_only_path: bool = openapi_json_url_only_path
        self.prefix: str = prefix or "/"
        self.pin_code: str = pin_code
        self.title: str = title or "Pait Doc"
        self.openapi: Type[OpenAPI] = openapi or OpenAPI
        self._is_gen: bool = False
        self._doc_fn_dict: Dict[str, Callable] = doc_fn_dict or default_doc_fn_dict
        self._doc_pait: Pait = self.pait_class(
            author=config.author or ("so1n",),
            status=config.status or PaitStatus.release,
            tag=(Tag("pait_doc", desc="pait default doc route"),),
            group="pait_doc",
        )
        self.gen_route(app)

    def _get_request_pin_code(
        self,
        r_pin_code: str = Query.i("", alias="pin-code"),
    ) -> Optional[str]:
        if self.pin_code and r_pin_code != self.pin_code:
            raise self.not_found_exc
        return r_pin_code

    @staticmethod
    def _get_request_template_map(extra_key: bool = False) -> Callable:
        def _get_request_template_map(
            url_dict: Dict[str, Any] = Query.i(
                default_factory=dict,
                raw_return=True,
                description="Set the template variable, for example, there is a template parameter token, "
                "then the requested parameter is template-token=xxx",
            )
        ) -> dict:
            template_dict: Dict[str, Any] = {}
            for k, v in url_dict.items():
                if k.startswith("template-"):
                    if extra_key:
                        k = k.replace("template-", "")
                    template_dict[k] = v
            return template_dict

        return _get_request_template_map

    def _gen_url_fn(self) -> Callable:
        def _get_openapi_json_url(
            r_pin_code: str = Depends.i(self._get_request_pin_code),
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map()),
        ) -> str:
            re = pait_context.get().app_helper.request.request_extend()
            _scheme: str = self.scheme or re.scheme
            if self.openapi_json_url_only_path:
                openapi_json_url: str = f"{'/'.join(re.path.split('/')[:-1])}/openapi.json"
            else:
                openapi_json_url = f"{_scheme}://{re.hostname}{'/'.join(re.path.split('/')[:-1])}/openapi.json"
            if r_pin_code:
                url_dict["pin-code"] = r_pin_code
            openapi_json_url += "?" + urlencode(url_dict)
            return openapi_json_url

        return _get_openapi_json_url

    @staticmethod
    def _get_doc_pait(
        pait_class: Type[Pait],
        plugin_list: Optional[List[PluginManager]] = None,
        post_plugin_list: Optional[List[PluginManager]] = None,
    ) -> Pait:
        return pait_class(
            author=config.author or ("so1n",),
            status=config.status or PaitStatus.release,
            tag=(Tag("pait_doc", desc="pait default doc route"),),
            group="pait_doc",
            plugin_list=plugin_list,
            post_plugin_list=post_plugin_list,
        )

    def _gen_route(self, app: APP_T) -> Any:  # type: ignore
        raise NotImplementedError()

    def _get_doc_route(self) -> Callable:
        dynamic_enum_class: Type[Enum] = DocEnum(  # type: ignore
            "DynamicEnum", {key: key for key in self._doc_fn_dict.keys()}
        )

        @self._doc_pait(
            pre_depend_list=[self._get_request_pin_code],
            response_model_list=[DocHtmlRespModel],
            feature_code=self.title,
        )
        def _doc_route(
            route_path: dynamic_enum_class = Path.i(description="doc ui html"),  # type: ignore
            url: str = Depends.i(self._gen_url_fn()),
        ) -> str:
            get_doc_route: Callable = self._doc_fn_dict[route_path.value]  # type: ignore
            return get_doc_route(url, title=self.title)

        _doc_route.__name__ = self.title + "doc_route"
        _doc_route.__qualname__ = _doc_route.__qualname__.replace("._doc_route", "." + _doc_route.__name__)
        return _doc_route

    def _get_openapi_route(self, app: APP_T) -> Callable:
        @self._doc_pait(
            pre_depend_list=[self._get_request_pin_code],
            response_model_list=[OpenAPIRespModel],
            feature_code=self.title,
        )
        def _openapi_route(
            url_dict: Dict[str, Any] = Depends.i(self._get_request_template_map(extra_key=True)),
        ) -> dict:
            re = pait_context.get().app_helper.request.request_extend()
            _scheme: str = self.scheme or re.scheme
            pait_dict: Dict[str, PaitCoreModel] = self.load_app(app)
            with TemplateContext(url_dict):
                pait_openapi: OpenAPI = OpenAPI(
                    pait_dict,
                    openapi_info_model=InfoModel(title=self.title),
                    server_model_list=[ServerModel(url=f"{_scheme}://{re.hostname}")],
                )
                return json.loads(pait_openapi.content())

        return _openapi_route

    def gen_route(self, app: APP_T) -> None:
        """Will remove on version 1.0"""
        if self._is_gen:
            raise RuntimeError("Doc route has been generated")
        self._gen_route(app)
        self._is_gen = True
