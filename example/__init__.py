from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


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


@asynccontextmanager
async def async_context_depend(
    uid: int = field.Query.i(description="user id", gt=10, lt=1000)
) -> AsyncGenerator[int, Any]:
    session: _DemoSession = _DemoSession(uid)
    try:
        print("context_depend init")
        session.create()
        yield session.uid
    except Exception:
        print("context_depend error")
    finally:
        print("context_depend exit")
        session.close()


@pait()
async def demo(
    uid: str = field.Depends.i(async_context_depend), is_raise: bool = field.Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
