from typing import List, Optional, Tuple, Type

from pait.model import PaitResponseModel, PaitStatus
from .auto_load_app import auto_load_app_class
from .flask import load_app as load_flask
from .flask import pait as flask_pait
from .starlette import load_app as load_starlette
from .starlette import pait as starlette_pait


def load_app(app):
    """Read data from the route that has been registered to `pait`
    Note:This is an implicit method
    """
    app_name: str = app.__class__.__name__
    if app_name == 'Flask':
        load_flask(app)
    elif app_name == 'Starlette':
        load_starlette(app)
    else:
        raise NotImplementedError(f'Pait not support:{app}')


def pait(
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: str = 'root',
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: List[Type[PaitResponseModel]] = None
):
    """provide parameter checks and type conversions for each routing function/cbv class"""
    load_class_app = auto_load_app_class()
    if load_class_app.__name__ == 'Flask':
        flask_pait(author, desc, status, group, tag, response_model_list)
    elif load_class_app.__name__ == 'Starlette':
        starlette_pait(author, desc, status, group, tag, response_model_list)
    else:
        raise NotImplementedError(f'Pait not support:{load_class_app}')

