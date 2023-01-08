import copy
from typing import Any, Type

from any_api.openapi.model.response_model import BaseResponseModel
from any_api.openapi.model.response_model import FileResponseModel as _FileResponseModel
from any_api.openapi.model.response_model import HtmlResponseModel as _HtmlResponseModel
from any_api.openapi.model.response_model import JsonResponseModel as _JsonResponseModel
from any_api.openapi.model.response_model import TextResponseModel as _TextResponseModel
from any_api.openapi.model.response_model import XmlResponseModel as _XmlResponseModel
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
]


class JsonResponseModel(_JsonResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel]) -> dict:
        return gen_example_dict_from_pydantic_base_model(model)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "JsonResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(cls.response_data, use_example_value=False)
            setattr(cls.response_data, "JsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


class XmlResponseModel(_XmlResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel]) -> dict:
        return gen_example_dict_from_pydantic_base_model(model)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "XmlResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(cls.response_data, use_example_value=False)
            setattr(cls.response_data, "XmlJsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


class TextResponseModel(_TextResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel]) -> dict:
        return gen_example_dict_from_pydantic_base_model(model)


class HtmlResponseModel(_HtmlResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel]) -> dict:
        return gen_example_dict_from_pydantic_base_model(model)


class FileResponseModel(_FileResponseModel):
    @classmethod
    def _get_example_dict(cls, model: Type[BaseModel]) -> dict:
        return gen_example_dict_from_pydantic_base_model(model)


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
