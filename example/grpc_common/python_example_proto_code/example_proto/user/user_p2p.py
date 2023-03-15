# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic(https://github.com/so1n/protobuf_to_pydantic)
# type: ignore

from enum import IntEnum

from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class SexType(IntEnum):
    man = 0
    women = 1


class CreateUserRequest(BaseModel):

    uid: str = FieldInfo(default="")
    user_name: str = FieldInfo(default="")
    password: str = FieldInfo(default="")
    sex: SexType = FieldInfo(default=0)


class DeleteUserRequest(BaseModel):

    uid: str = FieldInfo(default="")


class LoginUserRequest(BaseModel):

    uid: str = FieldInfo(default="")
    password: str = FieldInfo(default="")


class LoginUserResult(BaseModel):

    uid: str = FieldInfo(default="")
    user_name: str = FieldInfo(default="")
    token: str = FieldInfo(default="")


class LogoutUserRequest(BaseModel):

    uid: str = FieldInfo(default="")
    token: str = FieldInfo(default="")


class GetUidByTokenRequest(BaseModel):

    token: str = FieldInfo(default="")


class GetUidByTokenResult(BaseModel):

    uid: str = FieldInfo(default="")
