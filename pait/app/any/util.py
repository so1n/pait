from importlib import import_module
from typing import Any, Callable, Dict, List, Type

from typing_extensions import Literal

SupportAppLiteral = Literal["flask", "starlette", "sanic", "tornado"]
support_app_list: List[SupportAppLiteral] = ["flask", "starlette", "sanic", "tornado"]

sniffing_dict: Dict[Type, Callable[[Any], str]] = {}
framework_location_dict: Dict[str, str] = {}


def sniffing(app: Any) -> SupportAppLiteral:
    try:
        for base_class in [app.__class__, app.__class__.__base__]:
            app_name: str = base_class.__name__.lower()
            if app_name in support_app_list:
                return app_name  # type: ignore
            elif app_name == "application" and base_class.__module__ == "tornado.web":
                return "tornado"
    except Exception:
        pass

    if app.__class__ in sniffing_dict:
        return sniffing_dict[app.__class__](app)  # type: ignore

    raise NotImplementedError(f"Pait not support app: {app}, please check app")


def import_func_from_app(fun_name: str, app: Any = None, module_name: str = "") -> Callable:
    from pait.app.auto_load_app import auto_load_app_class

    if app:
        # support werkzeug LocalProxy
        _get_current_object = getattr(app, "_get_current_object", None)
        if _get_current_object:
            app = _get_current_object()

        app_name: str = sniffing(app)
    else:
        app_name = auto_load_app_class().__name__.lower()
    framework_location = framework_location_dict.get(app_name, "pait.app")
    if module_name:
        return getattr(import_module(f"{framework_location}.{app_name}.{module_name}"), fun_name)
    else:
        return getattr(import_module(f"{framework_location}.{app_name}"), fun_name)


def base_call_func(fun_name: str, *args: Any, app: Any = None, module_name: str = "", **kwargs: Any) -> Any:
    return import_func_from_app(fun_name, app=app, module_name=module_name)(*args, **kwargs)
