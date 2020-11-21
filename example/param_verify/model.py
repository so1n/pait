from dataclasses import dataclass, field
from enum import Enum
from typing import List

from pait.field import Depends, Header, Query
from pait.util import PaitBaseModel, PaitResponseModel
from pydantic import (
    BaseModel,
    conint,
    constr,
    Field
)


class TestPaitModel(PaitBaseModel):
    uid: conint(gt=10, lt=1000) = Query(description='用户uid')
    user_name: constr(min_length=2, max_length=4) = Query(description='用户名')
    user_agent: str = Header(key='user-agent', description='ua')


class UserModel(BaseModel):
    uid: conint(gt=10, lt=1000) = Field(123456, description='用户uid')
    user_name: constr(min_length=2, max_length=4) = Field(description='用户名')


class UserOtherModel(BaseModel):
    age: conint(gt=1, lt=100) = Field(description='年龄')


class SexEnum(Enum):
    man: str = 'man'
    woman: str = 'woman'


def demo_sub_depend(user_agent: str = Header(key='user-agent', description='ua')):
    print('sub_depend', user_agent)
    return user_agent


def demo_depend(user_agent: str = Depends(demo_sub_depend)):
    print('depend', user_agent)
    return user_agent


### response model

class ResponseModel(BaseModel):
    code: int = Field(0, description='状态码')
    msg: str = Field('success', description='状态信息')


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description='状态码')
    msg: str = Field('fail', description='状态信息')


class ResponseUserModel(ResponseModel):
    class _BaseModel(BaseModel):
        class Test(BaseModel):
            test_a: int
            test_b: str

        uid: conint(gt=10, lt=1000) = Field(123456, description='用户uid')
        user_name: constr(min_length=2, max_length=4) = Field(description='用户名')
        age: conint(gt=1, lt=100) = Field(description='年龄')
        content_type: str = Field(description='content-type')
        test: Test

    data: List[_BaseModel]


@dataclass()
class UserSuccessRespModel(PaitResponseModel):
    description: str = 'success response'
    header: dict = field(default_factory=lambda: {'cookie': 'xxx'})
    response_data: BaseModel = ResponseUserModel


@dataclass()
class FailRespModel(PaitResponseModel):
    description: str = 'fail response'
    response_data: BaseModel = ResponseFailModel
