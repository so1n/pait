import logging
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from typing import Any, AsyncGenerator, Generator, List, Tuple, Type

from pydantic import BaseModel, Field

from pait.field import Body, Depends, Header, Query
from pait.model.response import (
    PaitFileResponseModel,
    PaitHtmlResponseModel,
    PaitJsonResponseModel,
    PaitResponseModel,
    PaitTextResponseModel,
)


class _DemoSession(object):
    def __init__(self, uid: int) -> None:
        self._uid: int = uid
        self._status: bool = False

    @property
    def uid(self) -> int:
        if self._status:
            return self._uid
        else:
            raise RuntimeError("Session is close")

    def create(self) -> None:
        self._status = True

    def close(self) -> None:
        self._status = False


class TestPaitModel(BaseModel):
    uid: int = Query.i(description="user id", gt=10, lt=1000)
    user_name: str = Query.i(description="user name", min_length=2, max_length=4)
    user_agent: str = Header.i(alias="user-agent", description="user agent")
    age: int = Body.i(description="age", gt=1, lt=100)


class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000, example="123")
    user_name: str = Field(description="user name", min_length=2, max_length=4, example="so1n")


class UserOtherModel(BaseModel):
    age: int = Field(description="age", gt=1, lt=100, example=25)


class SexEnum(str, Enum):
    man: str = "man"
    woman: str = "woman"


def demo_sub_depend(
    user_agent: str = Header.i(alias="user-agent", description="user agent"),
    age: int = Body.i(description="age", gt=1, lt=100),
) -> Tuple[str, int]:
    return user_agent, age


def demo_depend(depend_tuple: Tuple[str, int] = Depends.i(demo_sub_depend)) -> Tuple[str, int]:
    return depend_tuple


@contextmanager
def context_depend(uid: int = Query.i(description="user id", gt=10, lt=1000)) -> Generator[int, Any, Any]:
    session: _DemoSession = _DemoSession(uid)
    try:
        session.create()
        yield session.uid
    except Exception:
        logging.error("context_depend error")
    finally:
        logging.info("context_depend exit")
        session.close()


@asynccontextmanager
async def async_context_depend(uid: int = Query.i(description="user id", gt=10, lt=1000)) -> AsyncGenerator[int, Any]:
    session: _DemoSession = _DemoSession(uid)
    try:
        session.create()
        yield session.uid
    except Exception:
        logging.error("context_depend error")
    finally:
        logging.info("context_depend exit")
        session.close()


# response model
class ResponseModel(BaseModel):
    code: int = Field(0, description="api code")
    msg: str = Field("success", description="api status msg")


class ResponseFailModel(ResponseModel):
    code: int = Field(1, description="api code")
    msg: str = Field("fail", description="api status msg")


class UserSuccessRespModel(PaitResponseModel):
    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(666, description="user id", gt=10, lt=1000)
            user_name: str = Field("mock_name", description="user name", min_length=2, max_length=10)
            age: int = Field(99, description="age", gt=1, lt=100)
            sex: SexEnum = Field(SexEnum.man, description="sex")
            content_type: str = Field("application/json", description="content-type")

            class Config:
                use_enum_values = True

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class UserSuccessRespModel2(PaitJsonResponseModel):
    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000, example=666)
            user_name: str = Field(example="mock_name", description="user name", min_length=2, max_length=10)
            multi_user_name: List[str] = Field(
                example=("mock_name",), description="user name", min_length=2, max_length=4
            )
            sex: SexEnum = Field(example=SexEnum.man, description="sex")
            age: int = Field(example=99, description="age", gt=1, lt=100)
            email: str = Field(example="example@so1n.me", description="user email")

            class Config:
                use_enum_values = True

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class UserSuccessRespModel3(PaitJsonResponseModel):
    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000)
            user_name: str = Field(description="user name", min_length=2, max_length=4)
            age: int = Field(description="age", gt=1, lt=100)
            email: str = Field(description="user email")

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class FailRespModel(PaitJsonResponseModel):
    description: str = "fail response"
    response_data: Type[BaseModel] = ResponseFailModel


class SuccessRespModel(PaitJsonResponseModel):
    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel


class TextRespModel(PaitTextResponseModel):
    header: dict = {"X-Example-Type": "text"}
    description: str = "text response"


class HtmlRespModel(PaitHtmlResponseModel):
    header: dict = {"X-Example-Type": "html"}
    description: str = "html response"


class FileRespModel(PaitFileResponseModel):
    header: dict = {"X-Example-Type": "file"}
    description: str = "file response"


class LoginRespModel(PaitJsonResponseModel):
    class ResponseModel(BaseModel):  # type: ignore
        class DataModel(BaseModel):
            token: str

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "login response"
    response_data: Type[BaseModel] = ResponseModel
