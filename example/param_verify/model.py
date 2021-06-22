from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Type

from pydantic import BaseModel, Field

from pait.field import Body, Depends, Header, Query
from pait.model.base_model import PaitBaseModel
from pait.model.response import PaitResponseModel


class TestPaitModel(PaitBaseModel):
    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_name: str = Query.i(description="user name", min_length=2, max_length=4)
    user_agent: str = Header.i(alias="user-agent", description="user agent")
    age: int = Body.i(description="age", gt=1, lt=100)


class UserModel(BaseModel):
    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_name: str = Query.i(description="user name", min_length=2, max_length=4)


class UserOtherModel(BaseModel):
    age: int = Field(description="age", gt=1, lt=100)


class SexEnum(Enum):
    man: str = "man"
    woman: str = "woman"


def demo_sub_depend(
    user_agent: str = Header.i(alias="user-agent", description="user agent"),
    age: int = Body.i(description="age", gt=1, lt=100),
) -> Tuple[str, int]:
    return user_agent, age


def demo_depend(depend_tuple: Tuple[str, int] = Depends.i(demo_sub_depend)) -> Tuple[str, int]:
    return depend_tuple


# response model
class ResponseModel(BaseModel):
    code: int = Field(0, description="api code")
    msg: str = Field("success", description="api status msg")


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description="api code")
    msg: str = Field("fail", description="api status msg")


class ResponseUserModel(ResponseModel):
    class _BaseModel(BaseModel):

        uid: int = Field(description="user id", gt=10, lt=1000)
        user_name: str = Field(description="user name", min_length=2, max_length=4)
        age: int = Field(description="age", gt=1, lt=100)
        content_type: str = Field(description="content-type")

    data: List[_BaseModel]


@dataclass()
class UserSuccessRespModel(PaitResponseModel):
    description: str = "success response"
    header: dict = field(default_factory=lambda: {"cookie": "xxx"})
    response_data: Optional[Type[BaseModel]] = ResponseUserModel


@dataclass()
class UserSuccessRespModel2(PaitResponseModel):
    class _ResponseUserModel(ResponseModel):
        class _BaseModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000)
            user_name: str = Field(description="user name", min_length=2, max_length=4)
            email: str = Field(description="user email")
            age: int = Field(description="age", gt=1, lt=100)

        data: _BaseModel

    description: str = "success response"
    header: dict = field(default_factory=lambda: {"cookie": "xxx"})
    response_data: Optional[Type[BaseModel]] = _ResponseUserModel


@dataclass()
class FailRespModel(PaitResponseModel):
    description: str = "fail response"
    response_data: Optional[Type[BaseModel]] = ResponseFailModel


@dataclass()
class SuccessRespModel(PaitResponseModel):
    description: str = "success response"
    response_data: Optional[Type[BaseModel]] = ResponseModel
