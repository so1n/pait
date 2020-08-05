from enum import Enum

from pait.field import Header, Depends
from pydantic import (
    BaseModel,
    conint,
    constr,
)


class UserModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


class UserOtherModel(BaseModel):
    age: conint(gt=1, lt=100)


class SexEnum(Enum):
    man: str = 'man'
    woman: str = 'woman'


def demo_sub_depend(user_agent: str = Header(key='user-agent')):
    print('sub_depend', user_agent)
    return user_agent


def demo_depend(user_agent: str = Depends(demo_sub_depend)):
    print('depend', user_agent)
    return user_agent
