# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic(https://github.com/so1n/protobuf_to_pydantic)
# type: ignore

import typing
from datetime import datetime

from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class LikeBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")
    like: bool = FieldInfo(default=False)
    uid: str = FieldInfo(default="")


class LikeBookMapRequest(BaseModel):

    like_map: typing.Dict[str, bool] = FieldInfo(default_factory=dict)
    uid: str = FieldInfo(default="")


class GetBookLikesRequest(BaseModel):

    isbn: typing.List[str] = FieldInfo(default_factory=list)


class GetBookLikesResult(BaseModel):

    isbn: str = FieldInfo(default="")
    book_like: int = FieldInfo(default=0)


class GetBookLikesListResult(BaseModel):

    result: typing.List[GetBookLikesResult] = FieldInfo(default_factory=list)


class CommentBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")
    content: str = FieldInfo(default="")
    uid: str = FieldInfo(default="")


class GetBookCommentRequest(BaseModel):

    isbn: str = FieldInfo(default="")
    next_create_time: datetime = FieldInfo(default_factory=datetime.now)
    limit: int = FieldInfo(default=0)


class GetBookCommentResult(BaseModel):

    isbn: str = FieldInfo(default="")
    content: str = FieldInfo(default="")
    uid: str = FieldInfo(default="")
    create_time: datetime = FieldInfo(default_factory=datetime.now)


class GetBookCommentListResult(BaseModel):

    result: typing.List[GetBookCommentResult] = FieldInfo(default_factory=list)
