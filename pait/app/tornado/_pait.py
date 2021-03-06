from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from tornado.web import RequestHandler

from pait.core import pait as _pait
from pait.model.response import PaitResponseModel
from pait.model.status import PaitStatus
from pait.util import gen_example_json_from_schema
from ._app_helper import AppHelper


__all__ = ["pait"]


def make_mock_response(pait_response: Type[PaitResponseModel]) -> Any:
    tornado_handle: RequestHandler = getattr(pait_response, "handle", None)
    if not tornado_handle:
        raise RuntimeError("Can not load Tornado handle")
    tornado_handle.set_status(pait_response.status_code[0])
    for key, value in pait_response.header.items():
        tornado_handle.set_header(key, value)
    if pait_response.media_type == "application/json" and pait_response.response_data:
        tornado_handle.write(gen_example_json_from_schema(pait_response.response_data.schema()))
        return
    else:
        raise NotImplementedError()


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
        make_mock_response_fn=make_mock_response,
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
