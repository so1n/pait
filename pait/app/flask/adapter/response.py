from typing import Any, Type

from flask import Response, jsonify, make_response

from pait.model.response import BaseResponseModel, JsonResponseModel


def gen_response(response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any) -> Any:
    if isinstance(response_value, Response):
        return response_value
    elif issubclass(response_model_class, JsonResponseModel):
        resp: Response = jsonify(response_value)
    else:
        resp = make_response(response_value)
        resp.mimetype = response_model_class.media_type
    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
    return resp


def set_info_to_response(resp: Response, response_model_class: Type[BaseResponseModel]) -> None:
    resp.mimetype = response_model_class.media_type
    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
