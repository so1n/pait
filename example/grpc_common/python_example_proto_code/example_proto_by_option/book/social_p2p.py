# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.1.7](https://github.com/so1n/protobuf_to_pydantic)
import typing
from datetime import datetime

from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, Field, root_validator
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

    _one_of_dict = {
        "GetBookCommentRequest._limit": {"fields": {"limit"}},
        "GetBookCommentRequest._next_create_time": {"fields": {"next_create_time"}},
    }
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)

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


class NestedGetBookLikesRequest(BaseModel):

    nested: GetBookLikesRequest = FieldInfo()
