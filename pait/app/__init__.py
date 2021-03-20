from typing import Callable, List, Optional, Tuple, Type

from pait.model import PaitResponseModel, PaitStatus

from .auto_load_app import auto_load_app_class  # type: ignore


def load_app(app) -> None:
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    app_name: str = app.__class__.__name__.lower()
    if app_name == "flask":
        from .flask import load_app  # type: ignore

        load_app(app)
    elif app_name == "starlette":
        from .starlette import load_app  # type: ignore

        load_app(app)
    else:
        raise NotImplementedError(f"Pait not support:{app}")


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: str = "root",
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None,
) -> Callable:
    """provide parameter checks and type conversions for each routing function/cbv class
    Note:This is an implicit method
    """
    load_class_app = auto_load_app_class()
    if load_class_app.__name__.lower() == "flask":
        from .flask import pait

        return pait(author, desc, status, group, tag, response_model_list)
    elif load_class_app.__name__.lower() == "starlette":
        from .starlette import pait

        return pait(author, desc, status, group, tag, response_model_list)
    else:
        raise NotImplementedError(f"Pait not support:{load_class_app}")
