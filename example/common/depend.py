import logging
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Tuple

from example.common.request_model import UserModel
from pait.field import Body, Depends, Header, Query


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


def demo_sub_depend(
    user_agent: str = Header.i(alias="user-agent", description="user agent"),
    age: int = Body.i(description="age", gt=1, lt=100),
) -> Tuple[str, int]:
    return user_agent, age


def demo_depend(depend_tuple: Tuple[str, int] = Depends.i(demo_sub_depend)) -> Tuple[str, int]:
    return depend_tuple


class GetUserDepend(object):
    user_name: str = Query.i()

    def __call__(self, uid: int = Query.i()) -> UserModel:
        return UserModel(uid=uid, user_name=self.user_name)


class AsyncGetUserDepend(object):
    user_name: str = Query.i()

    async def __call__(self, uid: int = Query.i()) -> UserModel:
        return UserModel(uid=uid, user_name=self.user_name)
