# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic(https://github.com/so1n/protobuf_to_pydantic)
# type: ignore

import typing
from datetime import datetime

from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class CreateBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")
    book_name: str = FieldInfo(default="")
    book_author: str = FieldInfo(default="")
    book_desc: str = FieldInfo(default="")
    book_url: str = FieldInfo(default="")


class DeleteBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")


class GetBookRequest(BaseModel):

    isbn: str = FieldInfo(default="")


class GetBookResult(BaseModel):

    isbn: str = FieldInfo(default="")
    book_name: str = FieldInfo(default="")
    book_author: str = FieldInfo(default="")
    book_desc: str = FieldInfo(default="")
    book_url: str = FieldInfo(default="")
    create_time: datetime = FieldInfo(default_factory=datetime.now)
    update_time: datetime = FieldInfo(default_factory=datetime.now)


class GetBookListRequest(BaseModel):

    next_create_time: datetime = FieldInfo(default_factory=datetime.now)
    limit: int = FieldInfo(default=0)


class GetBookListResult(BaseModel):

    result: typing.List[GetBookResult] = FieldInfo(default_factory=list)
