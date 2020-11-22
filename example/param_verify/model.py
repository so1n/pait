from dataclasses import dataclass, field
from enum import Enum
from typing import List

from pait.field import Depends, Header, Query
from pait.model import PaitResponseModel, PaitBaseModel
from pydantic import (
    BaseModel,
    conint,
    constr,
    Field
)


class TestPaitModel(PaitBaseModel):
    uid: conint(gt=10, lt=1000) = Query(description='user id')
    user_name: constr(min_length=2, max_length=4) = Query(description='user name')
    user_agent: str = Header(alias='user-agent', description='user agent')


class UserModel(BaseModel):
    uid: conint(gt=10, lt=1000) = Field(123456, description='user id')
    user_name: constr(min_length=2, max_length=4) = Field(description='user name')


class UserOtherModel(BaseModel):
    age: conint(gt=1, lt=100) = Field(description='age')


class SexEnum(Enum):
    man: str = 'man'
    woman: str = 'woman'


def demo_sub_depend(user_agent: str = Header(alias='user-agent', description='user agent')):
    print('sub_depend', user_agent)
    return user_agent


def demo_depend(user_agent: str = Depends(demo_sub_depend)):
    print('depend', user_agent)
    return user_agent


### response model

class ResponseModel(BaseModel):
    code: int = Field(0, description='api code')
    msg: str = Field('success', description='api status msg')


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description='api code')
    msg: str = Field('fail', description='api status msg')


class ResponseUserModel(ResponseModel):
    class _BaseModel(BaseModel):
        class Test(BaseModel):
            test_a: int
            test_b: str

        uid: conint(gt=10, lt=1000) = Field(123456, description='user id')
        user_name: constr(min_length=2, max_length=4) = Field(description='user name')
        age: conint(gt=1, lt=100) = Field(description='age')
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
