import warnings
from typing import Any, Optional, Type

from pydantic import BaseModel
from tornado.web import RequestHandler

from pait._pydanitc_adapter import model_dump
from pait.model.response import BaseResponseModel, FileResponseModel, JsonResponseModel


def _gen_response(
    tornado_handle: RequestHandler,
    response_value: Any,
    response_model_class: Type[BaseResponseModel],
    *args: Any,
    **kwargs: Any,
) -> Any:
    if issubclass(response_model_class, FileResponseModel):
        raise RuntimeError("FileResponseModel is not supported")
    set_info_to_response(tornado_handle, response_model_class)
    if isinstance(response_value, BaseModel):
        response_value = model_dump(response_value)
    tornado_handle.write(response_value)
    return None


def gen_response(
    tornado_handle: RequestHandler,
    response_value: Any,
    response_model_class: Type[BaseResponseModel],
    *args: Any,
    **kwargs: Any,
) -> Any:
    warnings.warn("This method will be removed after version 2.0", DeprecationWarning)
    return _gen_response(tornado_handle, response_value, response_model_class, *args, **kwargs)


def gen_unifiled_response(
    tornado_handle: RequestHandler,
    response_value: Any,
    *args: Any,
    response_model_class: Optional[Type[BaseResponseModel]] = None,
    **kwargs: Any,
) -> Any:
    """Compatible with different response values and generate responses that conform to response_model_class"""
    return _gen_response(tornado_handle, response_value, response_model_class or JsonResponseModel, *args, **kwargs)


def set_info_to_response(tornado_handle: RequestHandler, response_model_class: Type[BaseResponseModel]) -> None:
    tornado_handle.set_status(response_model_class.status_code[0])
    tornado_handle.set_header("Content-Type", response_model_class.media_type)
    if response_model_class.header is not None:
        for k, v in response_model_class.get_header_example_dict().items():
            tornado_handle.set_header(k, v)
