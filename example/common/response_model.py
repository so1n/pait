from typing import Generic, List, Type, TypeVar

from pydantic import BaseModel, Field

from example.common.request_model import SexEnum
from pait import _pydanitc_adapter
from pait.model.response import FileResponseModel, HtmlResponseModel, JsonResponseModel
from pait.model.response import ResponseModel as PaitResponseModel
from pait.model.response import TextResponseModel
from pait.openapi.openapi import LinksModel

T = TypeVar("T")


class ResponseModel(BaseModel):
    code: int = Field(0, description="api code")
    msg: str = Field("success", description="api status msg")


if _pydanitc_adapter.is_v1:
    from pydantic.generics import GenericModel

    class ResponseWithDataModel(ResponseModel, GenericModel, Generic[T]):  # type: ignore[no-redef]
        data: T = Field(description="success result")

else:

    class ResponseWithDataModel(ResponseModel, Generic[T]):  # type: ignore[no-redef]
        data: T = Field(description="success result")


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description="api code")
    msg: str = Field("fail", description="api status msg")


class UserSuccessRespModel(PaitResponseModel):
    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(666, description="user id", gt=10, lt=1000)
            user_name: str = Field("mock_name", description="user name", min_length=2, max_length=10)
            age: int = Field(99, description="age", gt=1, lt=100)
            sex: SexEnum = Field(SexEnum.man, description="sex")
            content_type: str = Field(description="content-type")

            class Config:
                use_enum_values = True

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class AAAUserSuccessRespModel(PaitResponseModel):
    class DataModel(BaseModel):
        uid: int = Field(666, description="user id", gt=10, lt=1000)
        user_name: str = Field("mock_name", description="user name", min_length=2, max_length=10)
        age: int = Field(99, description="age", gt=1, lt=100)
        sex: SexEnum = Field(SexEnum.man, description="sex")
        content_type: str = Field(description="content-type")

        class Config:
            use_enum_values = True

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseWithDataModel[DataModel]


class UserSuccessRespModel2(JsonResponseModel):
    class DataModel(BaseModel):
        uid: int = Field(description="user id", gt=10, lt=1000, example=666)
        user_name: str = Field(example="mock_name", description="user name", min_length=2, max_length=10)
        multi_user_name: List[str] = Field(example=["mock_name"], description="user name", min_length=1, max_length=10)
        sex: SexEnum = Field(example=SexEnum.man, description="sex")
        age: int = Field(example=99, description="age", gt=1, lt=100)
        email: str = Field(example="example@so1n.me", description="user email")

        class Config:
            use_enum_values = True

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseWithDataModel[DataModel]


class AutoCompleteRespModel(JsonResponseModel):
    class DataModel(BaseModel):
        class MusicModel(BaseModel):
            name: str = Field("")
            url: str = Field()
            singer: str = Field("")

        uid: int = Field(100, description="user id", gt=10, lt=1000)
        music_list: List[MusicModel] = Field(description="music list")
        image_list: List[dict] = Field(description="music list")

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseWithDataModel[DataModel]


class UserSuccessRespModel3(JsonResponseModel):
    class DataModel(BaseModel):
        uid: int = Field(description="user id", gt=10, lt=1000)
        user_name: str = Field(description="user name", min_length=2, max_length=4)
        age: int = Field(description="age", gt=1, lt=100)
        email: str = Field(description="user email")

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseWithDataModel[DataModel]


class FailRespModel(JsonResponseModel):
    description: str = "fail response"
    response_data: Type[BaseModel] = ResponseFailModel


class SuccessRespModel(JsonResponseModel):
    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class SimpleRespModel(JsonResponseModel):

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseWithDataModel[dict]


class TextRespModel(TextResponseModel):
    class HeaderModel(BaseModel):
        x_example_type: str = Field(default="text", alias="X-Example-Type")

    header: BaseModel = HeaderModel
    description: str = "text response"


class HtmlRespModel(HtmlResponseModel):
    class HeaderModel(BaseModel):
        x_example_type: str = Field(default="html", alias="X-Example-Type")

    header: BaseModel = HeaderModel
    description: str = "html response"


class FileRespModel(FileResponseModel):
    class HeaderModel(BaseModel):
        x_example_type: str = Field(default="file", alias="X-Example-Type")

    header: BaseModel = HeaderModel
    description: str = "file response"


class LoginRespModel(JsonResponseModel):
    class DataModel(BaseModel):
        token: str

    description: str = "login response"
    response_data: Type[BaseModel] = ResponseWithDataModel[DataModel]


link_login_token_model: LinksModel = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


class BadRequestRespModel(HtmlResponseModel):
    status_code = (400,)


class BadRequestTextRespModel(TextResponseModel):
    status_code = (400,)


class NotAuthenticated401RespModel(HtmlResponseModel):
    status_code = (401,)
    response_data = "Not authenticated"


class NotAuthenticated401TextRespModel(TextResponseModel):
    status_code = (401,)
    response_data = "Not authenticated"


class NotAuthenticated403RespModel(HtmlResponseModel):
    status_code = (403,)
    response_data = "Not authenticated"


class NotAuthenticated403TextRespModel(TextResponseModel):
    status_code = (403,)
    response_data = "Not authenticated"
