from typing import Any, Callable, Dict, TYPE_CHECKING
from importlib import import_module
from pait.app.base.util import sniffing


def import_func_from_app(fun_name: str, app: Any = None) -> Callable:
    from pait.app.auto_load_app import auto_load_app_class
    if app:
        app_name: str = sniffing(app)
    else:
        app_name = auto_load_app_class().__name__.lower()
    return getattr(import_module(f"pait.app.{app_name}"), fun_name)


def base_call_func(fun_name: str, *args: Any,app: Any = None,  **kwargs: Any) -> Any:
    return import_func_from_app(fun_name, app=app)(*args, **kwargs)
