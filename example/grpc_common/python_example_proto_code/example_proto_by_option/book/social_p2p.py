# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.1.7.3](https://github.com/so1n/protobuf_to_pydantic)
import typing
from datetime import datetime

from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, Field, root_validator


class LikeBookRequest(BaseModel):

    isbn: str = Field(default="")
    like: bool = Field(default=False)
    uid: str = Field(default="")


class LikeBookMapRequest(BaseModel):

    like_map: typing.Dict[str, bool] = Field(default_factory=dict)
    uid: str = Field(default="")


class GetBookLikesRequest(BaseModel):

    isbn: typing.List[str] = Field(default_factory=list)


class GetBookLikesResult(BaseModel):

    isbn: str = Field(default="")
    book_like: int = Field(default=0)


class GetBookLikesListResult(BaseModel):

    result: typing.List[GetBookLikesResult] = Field(default_factory=list)


class CommentBookRequest(BaseModel):

    isbn: str = Field(default="")
    content: str = Field(default="")
    uid: str = Field(default="")


class GetBookCommentRequest(BaseModel):

    _one_of_dict = {
        "GetBookCommentRequest._limit": {"fields": {"limit"}},
        "GetBookCommentRequest._next_create_time": {"fields": {"next_create_time"}},
    }
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)

    isbn: str = Field(default="")
    next_create_time: datetime = Field(default_factory=datetime.now)
    limit: int = Field(default=0)


class GetBookCommentResult(BaseModel):

    isbn: str = Field(default="")
    content: str = Field(default="")
    uid: str = Field(default="")
    create_time: datetime = Field(default_factory=datetime.now)


class GetBookCommentListResult(BaseModel):

    result: typing.List[GetBookCommentResult] = Field(default_factory=list)


class NestedGetBookLikesRequest(BaseModel):

    nested: GetBookLikesRequest = Field()
