from enum import Enum

from pydantic import BaseModel, Field

from pait.field import Body, Header, Query


class TestPaitModel(BaseModel):
    class UserInfo(BaseModel):
        user_name: str = Field(description="user name", min_length=2, max_length=4)
        age: int = Field(description="age", gt=1, lt=100)

    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_agent: str = Header.i(alias="user-agent", description="user agent")
    user_info: UserInfo = Body.i()


class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000, example="123")
    user_name: str = Field(description="user name", min_length=2, max_length=4, example="so1n")


class UserOtherModel(BaseModel):
    age: int = Field(description="age", gt=1, lt=100, example=25)


class SexEnum(str, Enum):
    man: str = "man"
    woman: str = "woman"
