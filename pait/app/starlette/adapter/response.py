from typing import Any, Type

from starlette.responses import JSONResponse, Response

from pait.model.response import BaseResponseModel, JsonResponseModel


def gen_response(response_value: Any, response_model_class: Type[BaseResponseModel], *args: Any, **kwargs: Any) -> Any:
    if isinstance(response_value, Response):
        return response_value
    elif issubclass(response_model_class, JsonResponseModel):
        resp: Response = JSONResponse(response_value)
    else:
        resp = Response(response_value, media_type=response_model_class.media_type)

    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
    return resp


def set_info_to_response(resp: Response, response_model_class: Type[BaseResponseModel]) -> None:
    resp.media_type = response_model_class.media_type
    resp.status_code = response_model_class.status_code[0]
    if response_model_class.header:
        resp.headers.update(response_model_class.get_header_example_dict())
