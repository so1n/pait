from contextlib import contextmanager
from typing import Any, Generator

from flask import Flask, Response, jsonify

from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException


def api_exception(exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    return jsonify({"data": str(exc)})


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
def context_depend(uid: int = field.Query.i(description="user id", gt=10, lt=1000)) -> Generator[int, Any, Any]:
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
def demo(uid: int = field.Depends.i(context_depend), is_raise: bool = field.Query.i(default=False)) -> Response:
    if is_raise:
        raise RuntimeError()
    return jsonify({"code": 0, "msg": uid})


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)


if __name__ == "__main__":
    app.run(port=8000)
