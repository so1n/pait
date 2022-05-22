from typing import Any, List

from pait.types import Literal

SupportAppLiteral = Literal["flask", "starlette", "sanic", "tornado"]
support_app_list: List[SupportAppLiteral] = ["flask", "starlette", "sanic", "tornado"]


def sniffing(app: Any) -> SupportAppLiteral:
    app_name: str = app.__class__.__name__.lower()
    if app_name in support_app_list:
        return app_name  # type: ignore
    elif app_name == "application" and app.__class__.__module__ == "tornado.web":
        return "tornado"
    else:
        raise NotImplementedError(f"Pait not support app name:{app_name}, please check app:{app}")
