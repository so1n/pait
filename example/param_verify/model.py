from enum import Enum

from pait.field import Depends, Header, Query, FactoryField
from pydantic import (
    BaseModel,
    conint,
    constr,
    Field
)


class TestPaitModel(BaseModel):
    uid: conint(gt=10, lt=1000) = FactoryField(Query(description='用户uid'))
    user_name: constr(min_length=2, max_length=4) = FactoryField(Query(description='用户名'))
    user_agent: str = FactoryField(Header(key='user-agent', description='ua'))


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
