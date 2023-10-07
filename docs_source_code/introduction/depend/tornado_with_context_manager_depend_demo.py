from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait
from pait.exceptions import TipException
from pait.openapi.doc_route import AddDocRoute


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
async def context_depend(uid: int = field.Query.i(description="user id", gt=10, lt=1000)) -> AsyncGenerator[int, Any]:
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


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc

        self.write({"data": str(exc)})
        self.finish()


class DemoHandler(_Handler):
    @pait()
    async def get(
        self, uid: int = field.Depends.i(context_depend), is_raise: bool = field.Query.i(default=False)
    ) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": uid})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
