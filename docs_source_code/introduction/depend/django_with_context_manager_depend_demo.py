import os
import sys
from contextlib import contextmanager
from typing import Any, Generator

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait


class _DemoSession(object):
    def __init__(self, uid: int) -> None:
        self._uid: int = uid
        self._status: bool = False

    @property
    def uid(self) -> int:
        if self._status:
            return self._uid
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
def demo(uid: int = field.Depends.i(context_depend), is_raise: bool = field.Query.i(default=False)) -> JsonResponse:
    if is_raise:
        raise RuntimeError()
    return JsonResponse({"code": 0, "msg": uid})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(
        urlpatterns,
        "docs_source_code.introduction.depend.django_with_context_manager_depend_demo_urlconf",
    )
