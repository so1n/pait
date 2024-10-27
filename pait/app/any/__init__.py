from dataclasses import MISSING
from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

from typing_extensions import NoReturn, Unpack

from pait.app.any.util import base_call_func, sniffing
from pait.app.auto_load_app import auto_load_app_class
from pait.app.base.simple_route import SimpleRoute
from pait.model.core import PaitCoreModel

if TYPE_CHECKING:
    from pait.core import PaitCreateSubParamTypedDict


_NotFoundFrameworkException = RuntimeError(
    "The web framework to use cannot be found automatically, please specify it manually"
)


class Empty(object):
    """Any call is guaranteed to throw an error"""

    def __int__(self) -> NoReturn:
        raise _NotFoundFrameworkException  # pragma: no cover

    def __setattr__(self, key: Any, value: Any) -> NoReturn:
        raise _NotFoundFrameworkException  # pragma: no cover

    def __getattr__(self, item: Any) -> NoReturn:
        raise _NotFoundFrameworkException  # pragma: no cover

    def __call__(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise _NotFoundFrameworkException  # pragma: no cover


try:
    load_class_app: Any = auto_load_app_class()
    pait_app_path: str = "pait.app." + load_class_app.__name__.lower()
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from pait.core import Pait as _Pait

    Pait: "_Pait" = getattr(import_module(pait_app_path), "Pait")
    http_exception = getattr(import_module(pait_app_path), "http_exception")
except RuntimeError:  # pragma: no cover
    # Automatic loading of classes, loading failure when the user can not use
    load_class_app = Empty()
    Pait = Empty()  # type: ignore
    pait_app_path = ""  # pragma: no cover
    http_exception = Empty()  # type: ignore


def load_app(
    app: Any,
    auto_load_route: bool = False,
    override_operation_id: bool = False,
    overwrite_already_exists_data: bool = False,
    auto_cbv_handle: bool = True,
) -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    return base_call_func(
        "load_app",
        app,
        app=app,
        auto_load_route=auto_load_route,
        override_operation_id=override_operation_id,
        overwrite_already_exists_data=overwrite_already_exists_data,
        auto_cbv_handle=auto_cbv_handle,
    )


def pait(**kwargs: Unpack["PaitCreateSubParamTypedDict"]) -> Callable:
    """provide parameter checks and type conversions for each routing function/cbv class
    Note:This is an implicit method
    """
    if not pait_app_path:
        raise RuntimeError("Auto load app fail")  # pragma: no cover
    _pait: Optional[Callable] = getattr(import_module(pait_app_path), "pait")
    if not _pait:
        raise NotImplementedError(f"Pait not support:{load_class_app}")
    return _pait(**kwargs)


def set_app_attribute(app: Any, key: str, value: Any) -> None:
    base_call_func("set_app_attribute", app, key, value, app=app)


def get_app_attribute(app: Any, key: str, default_value: Any = MISSING) -> Any:
    return base_call_func("get_app_attribute", app, key, default_value, app=app)


def add_simple_route(app: Any, simple_route: "SimpleRoute") -> None:
    base_call_func("add_simple_route", app, simple_route, app=app)


def add_multi_simple_route(
    app: Any, *simple_route_list: "SimpleRoute", prefix: str = "/", title: str = "", **kwargs: Any
) -> None:
    base_call_func("add_multi_simple_route", app, *simple_route_list, app=app, prefix=prefix, title=title, **kwargs)
