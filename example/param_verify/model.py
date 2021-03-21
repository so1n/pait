from dataclasses import dataclass, field
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from pait.field import Depends, Header, Query
from pait.model import PaitBaseModel, PaitResponseModel


class TestPaitModel(PaitBaseModel):
    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_name: str = Query.i(description="user name", min_length=2, max_length=4)
    user_agent: str = Header.i(alias="user-agent", description="user agent")


class UserModel(BaseModel):
    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_name: str = Query.i(description="user name", min_length=2, max_length=4)


class UserOtherModel(BaseModel):
    age: int = Field(description="age", gt=1, lt=100)


class SexEnum(Enum):
    man: str = "man"
    woman: str = "woman"


def demo_sub_depend(user_agent: str = Header.i(alias="user-agent", description="user agent")) -> str:
    print("sub_depend", user_agent)
    return user_agent


def demo_depend(user_agent: str = Depends.i(demo_sub_depend)) -> str:
    print("depend", user_agent)
    return user_agent


### response model


class ResponseModel(BaseModel):
    code: int = Field(0, description="api code")
    msg: str = Field("success", description="api status msg")


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description="api code")
    msg: str = Field("fail", description="api status msg")


class ResponseUserModel(ResponseModel):
    class _BaseModel(BaseModel):
        class Test(BaseModel):
            test_a: int
            test_b: str

        uid: int = Query.i(description="user id", gt=10, lt=1000)
        user_name: str = Query.i(description="user name", min_length=2, max_length=4)
        age: int = Field(description="age", gt=1, lt=100)
        content_type: str = Field(description="content-type")
        test: Test

    data: List[_BaseModel]


@dataclass()
class UserSuccessRespModel(PaitResponseModel):
    description: str = "success response"
    header: dict = field(default_factory=lambda: {"cookie": "xxx"})
    response_data: BaseModel = ResponseUserModel


@dataclass()
class FailRespModel(PaitResponseModel):
    description: str = "fail response"
    response_data: BaseModel = ResponseFailModel


@dataclass()
class SuccessRespModel(PaitResponseModel):
    description: str = "success response"
    response_data: BaseModel = ResponseModel
