from abc import ABC
from typing import Any, Optional, Type

from tornado.web import Application, RequestHandler

from pait.app.base.doc_route import AddDocRoute as _AddDocRoute
from pait.app.base.doc_route import OpenAPI
from pait.app.tornado._simple_route import MediaTypeEnum, SimpleRoute, add_multi_simple_route

from ._load_app import load_app
from ._pait import Pait

__all__ = ["add_doc_route", "AddDocRoute"]


class NotFound(Exception):
    pass


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


class AddDocRoute(_AddDocRoute[Application]):
    not_found_exc: Exception = NotFound()
    pait_class = Pait
    load_app = staticmethod(load_app)

    def _gen_route(self, app: Application) -> Any:
        add_multi_simple_route(
            app,
            SimpleRoute(
                url=r"/(?P<route_path>\w+)",
                route=self._get_doc_route(),
                methods=["GET"],
                media_type_enum=MediaTypeEnum.html,
            ),
            SimpleRoute(url="/openapi.json", route=self._get_openapi_route(app), methods=["GET"]),
            prefix=self.prefix,
            title=self.title,
            request_handler=BaseHandle,
        )


def add_doc_route(
    app: Application,
    scheme: Optional[str] = None,
    openapi_json_url_only_path: bool = False,
    prefix: str = "",
    pin_code: str = "",
    title: str = "",
    openapi: Optional[Type["OpenAPI"]] = None,
    project_name: str = "",
) -> None:
    AddDocRoute(
        scheme=scheme,
        openapi_json_url_only_path=openapi_json_url_only_path,
        prefix=prefix,
        pin_code=pin_code,
        title=title,
        openapi=openapi,
        project_name=project_name,
        app=app,
    )
