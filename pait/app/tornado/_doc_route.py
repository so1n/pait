import asyncio
from abc import ABC
from typing import Any, Dict, List, Optional

from tornado.web import Application, RequestHandler

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.tornado.plugin.base import JsonProtocol

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class WriteRespPlugin(JsonProtocol):
    """Used for compatible routing functions that do not belong to coro and cannot actively call the
    Request Handler.write method"""

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super(WriteRespPlugin, self).__call__(*args, **kwargs)
        if asyncio.iscoroutine(response):
            response = await response
        tornado_handle: RequestHandler = args[0]
        return self.gen_response(tornado_handle, response)


class NotFound(Exception):
    pass


class AddDocRoute(_AddDocRoute[Application, None]):
    not_found_exc: Exception = NotFound()
    pait_class = Pait
    html_response = staticmethod(lambda x: x)
    json_response = staticmethod(lambda x: x)
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Application) -> Any:
        self._doc_pait: Pait = self._doc_pait.create_sub_pait(append_plugin_list=[WriteRespPlugin.build()])
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

        class GetdocHtmlHandle(BaseHandle, ABC):
            get = self._get_doc_route()

        class OpenApiHandle(BaseHandle, ABC):
            get = self._get_openapi_route(app)

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
                (r"{}openapi.json".format(prefix), OpenApiHandle),
                (r"{}(?P<route_path>\w+)".format(prefix), GetdocHtmlHandle),
            ]
        )
        from tornado.web import AnyMatches, Rule, _ApplicationRouter

        app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])


def add_doc_route(
    app: Application,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
    project_name: str = "",
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        open_api_tag_list=open_api_tag_list,
        project_name=project_name,
        app=app,
    )
