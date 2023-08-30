from typing import Any, Type

from tornado.web import RequestHandler

from pait.model.response import BaseResponseModel


def gen_response(response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any) -> Any:
    if response_value is None:
        return None
    tornado_handle: RequestHandler = args[0]
    tornado_handle.set_status(response_model_class.status_code[0])

    if response_model_class.header is not None:
        for k, v in response_model_class.get_header_example_dict().items():
            tornado_handle.set_header(k, v)
    tornado_handle.set_header("Content-Type", response_model_class.media_type)
    tornado_handle.write(response_value)
    return None


def set_info_to_response(tornado_handle: RequestHandler, response_model_class: Type[BaseResponseModel]) -> None:
    tornado_handle.set_status(response_model_class.status_code[0])
    tornado_handle.set_header("Content-Type", response_model_class.media_type)
    if response_model_class.header is not None:
        for k, v in response_model_class.get_header_example_dict().items():
            tornado_handle.set_header(k, v)
