from importlib import import_module
from typing import Any, Callable, List

from typing_extensions import Literal

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


def import_func_from_app(fun_name: str, app: Any = None, module_name: str = "") -> Callable:
    from pait.app.auto_load_app import auto_load_app_class

    if app:
        app_name: str = sniffing(app)
    else:
        app_name = auto_load_app_class().__name__.lower()
    if module_name:
        return getattr(import_module(f"pait.app.{app_name}.{module_name}"), fun_name)
    else:
        return getattr(import_module(f"pait.app.{app_name}"), fun_name)


def base_call_func(fun_name: str, *args: Any, app: Any = None, module_name: str = "", **kwargs: Any) -> Any:
    return import_func_from_app(fun_name, app=app, module_name=module_name)(*args, **kwargs)
