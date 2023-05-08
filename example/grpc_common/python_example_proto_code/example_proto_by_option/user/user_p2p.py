# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.1.7.3](https://github.com/so1n/protobuf_to_pydantic)
from enum import IntEnum

from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel, Field


class SexType(IntEnum):
    man = 0
    women = 1


class CreateUserRequest(BaseModel):

    uid: str = Field(example="10086", title="UID", description="user union id")
    user_name: str = Field(default="", example="so1n", description="user name", min_length=1, max_length=10)
    password: str = Field(
        default="", example="123456", alias="pw", description="user password", min_length=6, max_length=18
    )
    sex: SexType = Field(default=0)


class DeleteUserRequest(BaseModel):

    uid: str = Field(default="")


class LoginUserRequest(BaseModel):

    uid: str = Field(default="")
    password: str = Field(default="")


class LoginUserResult(BaseModel):

    uid: str = Field(default="", example="10086", title="UID", description="user union id")
    user_name: str = Field(default="", example="so1n", description="user name", min_length=1, max_length=10)
    token: str = Field(default="", description="user token")


class LogoutUserRequest(BaseModel):

    uid: str = Field(default="")


class GetUidByTokenRequest(BaseModel):

    token: str = Field(default="")


class GetUidByTokenResult(BaseModel):

    uid: str = Field(default="")
