# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic(https://github.com/so1n/protobuf_to_pydantic)
from enum import IntEnum

from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo


class SexType(IntEnum):
    man = 0
    women = 1


class CreateUserRequest(BaseModel):

    uid: str = FieldInfo(example="10086", title="UID", description="user union id")
    user_name: str = FieldInfo(default="", example="so1n", description="user name", min_length=1, max_length=10)
    password: str = FieldInfo(
        default="", example="123456", alias="pw", description="user password", min_length=6, max_length=18
    )
    sex: SexType = FieldInfo(default=0)


class DeleteUserRequest(BaseModel):

    uid: str = FieldInfo(default="")


class LoginUserRequest(BaseModel):

    uid: str = FieldInfo(default="")
    password: str = FieldInfo(default="")


class LoginUserResult(BaseModel):

    uid: str = FieldInfo(default="", example="10086", title="UID", description="user union id")
    user_name: str = FieldInfo(default="", example="so1n", description="user name", min_length=1, max_length=10)
    token: str = FieldInfo(default="", description="user token")


class LogoutUserRequest(BaseModel):

    uid: str = FieldInfo(default="")


class GetUidByTokenRequest(BaseModel):

    token: str = FieldInfo(default="")


class GetUidByTokenResult(BaseModel):

    uid: str = FieldInfo(default="")
