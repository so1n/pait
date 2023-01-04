import copy
from typing import Any

from any_api.openapi.model.response_model import BaseResponseModel, FileResponseModel, HtmlResponseModel
from any_api.openapi.model.response_model import JsonResponseModel as _JsonResponseModel
from any_api.openapi.model.response_model import TextResponseModel
from any_api.openapi.model.response_model import XmlResponseModel as _XmlResponseModel

from pait.util import gen_example_dict_from_pydantic_base_model

__all__ = [
    "ResponseModel",
    "PaitResponseModel",
    "BaseResponseModel",
    "HtmlResponseModel",
    "PaitHtmlResponseModel",
    "JsonResponseModel",
    "PaitJsonResponseModel",
    "FileResponseModel",
    "PaitFileResponseModel",
    "TextResponseModel",
    "PaitTextResponseModel",
    "XmlResponseModel",
    "PaitXmlResponseModel",
]


class JsonResponseModel(_JsonResponseModel):
    @classmethod
    def get_example_value(cls, **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(cls.response_data)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "JsonResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(cls.response_data, use_example_value=False)
            setattr(cls.response_data, "JsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


class XmlResponseModel(_XmlResponseModel):
    @classmethod
    def get_example_value(cls, **extra: Any) -> dict:
        return gen_example_dict_from_pydantic_base_model(cls.response_data)

    @classmethod
    def get_default_dict(cls, **extra: Any) -> dict:
        default_dict: dict = getattr(cls.response_data, "XmlResponseModel_default_dict", {})
        if not default_dict:
            default_dict = gen_example_dict_from_pydantic_base_model(cls.response_data, use_example_value=False)
            setattr(cls.response_data, "XmlJsonResponseModel_default_dict", default_dict)
        return copy.deepcopy(default_dict)


###################################
# Compatible with old version API #
###################################
class PaitJsonResponseModel(JsonResponseModel):
    pass


class ResponseModel(JsonResponseModel):
    pass


class PaitResponseModel(JsonResponseModel):
    """PaitJsonResponseModel alias Compatible versions below 0.7"""


class PaitTextResponseModel(TextResponseModel):
    pass


class PaitHtmlResponseModel(HtmlResponseModel):
    pass


class PaitXmlResponseModel(XmlResponseModel):
    pass


class PaitFileResponseModel(FileResponseModel):
    pass
