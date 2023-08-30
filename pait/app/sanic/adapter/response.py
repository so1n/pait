from typing import Any, Type

from sanic.response import BaseHTTPResponse, HTTPResponse, json

from pait.model.response import BaseResponseModel, JsonResponseModel


def gen_response(response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any) -> Any:
    if isinstance(response_value, BaseHTTPResponse):
        return response_value
    elif issubclass(response_model_class, JsonResponseModel):
        resp: BaseHTTPResponse = json(response_value)
    else:
        resp = HTTPResponse(response_value)
        resp.content_type = response_model_class.media_type

    resp.status = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
    return resp


def set_info_to_response(resp: BaseHTTPResponse, response_model_class: Type[BaseResponseModel]) -> None:
    resp.content_type = response_model_class.media_type
    resp.status = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
