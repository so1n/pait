from typing import Callable, Dict, List, Optional, Tuple, Type

from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.core import pait as _pait
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from ._app_helper import AppHelper

__all__ = ["pait"]


def pait(
    # param check
    at_most_one_of_list: Optional[List[List[str]]] = None,
    required_by: Optional[Dict[str, List[str]]] = None,
    # doc
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
) -> Callable:
    """Help starlette provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        author=author,
        desc=desc,
        summary=summary,
        name=name,
        status=status,
        group=group,
        tag=tag,
        response_model_list=response_model_list,
        at_most_one_of_list=at_most_one_of_list,
        required_by=required_by,
    )
