import json
from typing import Callable, Dict, List, Optional, Tuple, Type

from flask import Response, jsonify
from pydantic import BaseConfig

from pait.core import pait as _pait
from pait.g import config
from pait.model import response
from pait.model.status import PaitStatus

from ._app_helper import AppHelper

__all__ = ["pait"]


def make_mock_response(pait_response: Type[response.PaitBaseResponseModel]) -> Response:
    if issubclass(pait_response, response.PaitJsonResponseModel):
        resp: Response = jsonify(json.loads(pait_response.get_example_value(json_encoder_cls=config.json_encoder)))
    else:
        raise NotImplementedError()
    resp.status_code = pait_response.status_code[0]
    if pait_response.header:
        resp.headers.update(pait_response.header)  # type: ignore
    return resp


def pait(
    # param check
    at_most_one_of_list: Optional[List[List[str]]] = None,
    required_by: Optional[Dict[str, List[str]]] = None,
    pre_depend_list: Optional[List[Callable]] = None,
    # doc
    author: Optional[Tuple[str]] = None,
    desc: Optional[str] = None,
    summary: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[PaitStatus] = None,
    group: Optional[str] = None,
    tag: Optional[Tuple[str, ...]] = None,
    enable_mock_response: bool = False,
    response_model_list: Optional[List[Type[response.PaitBaseResponseModel]]] = None,
    pydantic_model_config: Optional[Type[BaseConfig]] = None,
) -> Callable:
    """Help flask provide parameter checks and type conversions for each routing function/cbv class"""
    return _pait(
        AppHelper,
        make_mock_response_fn=make_mock_response,
        author=author,
        desc=desc,
        name=name,
        summary=summary,
        status=status,
        group=group,
        tag=tag,
        enable_mock_response=enable_mock_response,
        response_model_list=response_model_list,
        pre_depend_list=pre_depend_list,
        at_most_one_of_list=at_most_one_of_list,
        required_by=required_by,
        pydantic_model_config=pydantic_model_config,
    )
