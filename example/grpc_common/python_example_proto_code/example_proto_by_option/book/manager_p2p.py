# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.1.7](https://github.com/so1n/protobuf_to_pydantic)
import typing
from datetime import datetime

from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, Field, root_validator
from pydantic.fields import FieldInfo

from pait.field import Query


class CreateBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")
    book_name: str = FieldInfo(default="")
    book_author: str = FieldInfo(default="")
    book_desc: str = FieldInfo(default="")
    book_url: str = FieldInfo(default="")


class DeleteBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")


class GetBookRequest(BaseModel):

    isbn: str = Query(default="")
    not_use_field1: str = FieldInfo(default="")
    not_use_field2: str = FieldInfo(default="")


class GetBookResult(BaseModel):

    isbn: str = FieldInfo(default="")
    book_name: str = FieldInfo(default="")
    book_author: str = FieldInfo(default="")
    book_desc: str = FieldInfo(default="")
    book_url: str = FieldInfo(default="")
    create_time: datetime = FieldInfo(default_factory=datetime.now)
    update_time: datetime = FieldInfo(default_factory=datetime.now)


class GetBookListRequest(BaseModel):

    _one_of_dict = {"GetBookListRequest._next_create_time": {"fields": {"next_create_time"}}}
    _check_one_of = root_validator(pre=True, allow_reuse=True)(check_one_of)

    next_create_time: datetime = FieldInfo(default_factory=datetime.now)
    limit: int = FieldInfo(default=0)


class GetBookListResult(BaseModel):

    result: typing.List[GetBookResult] = FieldInfo(default_factory=list)
