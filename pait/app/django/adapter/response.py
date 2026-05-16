import warnings
from typing import Any, Optional, Type

from django.http import FileResponse, HttpResponse, JsonResponse
from pydantic import BaseModel

from pait._pydanitc_adapter import model_dump
from pait.model.response import BaseResponseModel, FileResponseModel, JsonResponseModel


def _gen_response(
    response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any
) -> HttpResponse:
    if isinstance(response_value, HttpResponse):
        return response_value
    elif issubclass(response_model_class, JsonResponseModel):
        if isinstance(response_value, BaseModel):
            response_value = model_dump(response_value)
        resp = JsonResponse(response_value, safe=isinstance(response_value, dict))
    elif issubclass(response_model_class, FileResponseModel):
        if isinstance(response_value, FileResponse):
            resp = response_value
        else:
            raise RuntimeError("FileResponseModel is not supported")
    else:
        resp = HttpResponse(response_value, content_type=response_model_class.media_type)
    set_info_to_response(resp, response_model_class)
    return resp


def gen_response(
    response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any
) -> HttpResponse:
    warnings.warn("This method will be removed after version 2.0", DeprecationWarning)
    return _gen_response(response_value, response_model_class, *args, **kwargs)


def gen_unifiled_response(
    response_value: Any, *args: Any, response_model_class: Optional[Type[BaseResponseModel]] = None, **kwargs: Any
) -> HttpResponse:
    """Compatible with different response values and generate responses that conform to response_model_class"""
    return _gen_response(response_value, response_model_class or JsonResponseModel, *args, **kwargs)


def set_info_to_response(resp: HttpResponse, response_model_class: Type[BaseResponseModel]) -> None:
    resp.headers["Content-Type"] = response_model_class.media_type
    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        for key, value in response_model_class.get_header_example_dict().items():
            resp.headers[key] = value
