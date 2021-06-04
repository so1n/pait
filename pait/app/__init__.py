from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pait.model import PaitCoreModel, PaitResponseModel, PaitStatus

from .auto_load_app import auto_load_app_class  # type: ignore


def load_app(app: Any, project_name: str = "") -> Dict[str, PaitCoreModel]:
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    app_name: str = app.__class__.__name__.lower()
    if app_name == "flask":
        from .flask import load_app  # type: ignore

        return load_app(app, project_name)
    elif app_name == "starlette":
        from .starlette import load_app  # type: ignore

        return load_app(app, project_name)
    elif app_name == "sanic":
        from .sanic import load_app  # type: ignore

        return load_app(app, project_name)
    elif app_name == "application" and app.__class__.__module__ == "tornado.web":
        from .tornado import load_app  # type: ignore

        return load_app(app, project_name)
    else:
        raise NotImplementedError(f"Pait not support:{app}")


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: str = "root",
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None,
) -> Callable:
    """provide parameter checks and type conversions for each routing function/cbv class
    Note:This is an implicit method
    """
    load_class_app = auto_load_app_class()
    app_name: str = load_class_app.__name__.lower()
    if app_name == "flask":
        from .flask import pait as _pait
    elif app_name == "starlette":
        from .starlette import pait as _pait  # type: ignore
    elif app_name == "sanic":
        from .sanic import pait as _pait  # type: ignore
    elif app_name == "tornado":
        from .tornado import pait as _pait  # type: ignore
    else:
        raise NotImplementedError(f"Pait not support:{load_class_app}")
    return _pait(author, desc, summary, status, group, tag, response_model_list)
