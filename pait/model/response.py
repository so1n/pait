import copy
from typing import Any, Dict, Optional, Type

from any_api.openapi.model.responses import BaseResponseModel
from any_api.openapi.model.responses import FileResponseModel as _FileResponseModel
from any_api.openapi.model.responses import HtmlResponseModel as _HtmlResponseModel
from any_api.openapi.model.responses import JsonResponseModel as _JsonResponseModel
from any_api.openapi.model.responses import TextResponseModel as _TextResponseModel
from any_api.openapi.model.responses import XmlResponseModel as _XmlResponseModel
from pydantic import BaseModel

from pait.util import gen_example_dict_from_pydantic_base_model

__all__ = [
    "ResponseModel",
    "PaitResponseModel",
    "BaseResponseModel",
    "HtmlResponseModel",
    "HtmlResponseModel",
    "JsonResponseModel",
    "JsonResponseModel",
    "FileResponseModel",
    "FileResponseModel",
    "TextResponseModel",
    "TextResponseModel",
    "XmlResponseModel",
    "XmlResponseModel",
    "HttpStatusCodeBaseModel",
    "Http400RespModel",
    "Http401RespModel",
    "Http403RespModel",
    "Http404RespModel",
    "Http405RespModel",
    "Http406RespModel",
    "Http407RespModel",
    "Http408RespModel",
    "Http429RespModel",
]


class JsonResponseModel(_JsonResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel], **kwargs: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(model, **kwargs)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "JsonResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(
                cls.response_data, example_column_name=extra.pop("example_column_name", "")
            )
            setattr(cls.response_data, "JsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


class XmlResponseModel(_XmlResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel], **kwargs: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(model, **kwargs)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "XmlResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(
                cls.response_data, example_column_name=extra.pop("example_column_name", "")
            )
            setattr(cls.response_data, "XmlJsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


class TextResponseModel(_TextResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel], **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(model, **extra)


class HtmlResponseModel(_HtmlResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel], **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(model, **extra)


class FileResponseModel(_FileResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel], **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(model, **extra)


###################################
# Compatible with old version API #
###################################
class PaitJsonResponseModel(JsonResponseModel):
    pass


class ResponseModel(JsonResponseModel):
    pass


class PaitResponseModel(JsonResponseModel):
    """JsonResponseModel alias Compatible versions below 0.7"""


class PaitTextResponseModel(TextResponseModel):
    pass


class PaitHtmlResponseModel(HtmlResponseModel):
    pass


class PaitXmlResponseModel(XmlResponseModel):
    pass


class PaitFileResponseModel(FileResponseModel):
    pass


# Only define the status code that Pait will use internally, the user needs to define it through config.init config
http_status_code_dict: Dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Accepted",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    429: "Too Many Requests",
}


class HttpStatusCodeBaseModel(BaseResponseModel):
    response_data = None

    @classmethod
    def clone(
        cls, resp_model: Type[BaseResponseModel], status_code: Optional[int] = None, response_data: Any = None
    ) -> "Type[HttpStatusCodeBaseModel]":
        status_code = status_code or cls.status_code[0]
        response_data = response_data or http_status_code_dict.get(status_code, "") or cls.response_data
        if issubclass(resp_model, HtmlResponseModel):
            response_data = f"<h1>{response_data}<h1/>"
        resp_model_type = resp_model.__class__(  # type: ignore
            f"Http{status_code}RespModel",
            (
                resp_model,
                cls,
            ),
            {}
            # {"clone": cls.clone},
        )
        resp_model_type.status_code = (status_code,)
        resp_model_type.response_data = response_data
        return resp_model_type


Http400RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=400)
Http401RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=401)
Http403RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=403)
Http404RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=404)
Http405RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=405)
Http406RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=406)
Http407RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=407)
Http408RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=408)
Http429RespModel = HttpStatusCodeBaseModel.clone(resp_model=HtmlResponseModel, status_code=429)
