import warnings
from typing import Any, Optional, Type

from flask import Response, jsonify, make_response
from pydantic import BaseModel

from pait._pydanitc_adapter import model_dump
from pait.model.response import BaseResponseModel, FileResponseModel, JsonResponseModel


def _gen_response(
    response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any
) -> Response:
    if isinstance(response_value, Response):
        return response_value
    elif issubclass(response_model_class, JsonResponseModel):
        if isinstance(response_value, BaseModel):
            response_value = model_dump(response_value)
        resp: Response = jsonify(response_value)
    elif issubclass(response_model_class, FileResponseModel):
        raise RuntimeError("FileResponseModel is not supported")
    else:
        resp = make_response(response_value)
    set_info_to_response(resp, response_model_class)
    return resp


def gen_response(
    response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any
) -> Response:
    warnings.warn("This method will be removed after version 2.0", DeprecationWarning)
    return _gen_response(response_value, response_model_class, *args, **kwargs)


def gen_unifiled_response(
    response_value: Any, *args: Any, response_model_class: Optional[Type[BaseResponseModel]] = None, **kwargs: Any
) -> Response:
    """Compatible with different response values and generate responses that conform to response_model_class"""
    return _gen_response(response_value, response_model_class or JsonResponseModel, *args, **kwargs)


def set_info_to_response(resp: Response, response_model_class: Type[BaseResponseModel]) -> None:
    resp.mimetype = response_model_class.media_type
    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
