import logging
import time
from contextlib import contextmanager
from pprint import pprint
from typing import Callable, Generator

from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from starlette.testclient import TestClient
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from benchmarks.diff_use_pait import _flask, _sanic, _starlette, _tornado

state_result = {
    "flask": {"raw": 0.0, "use-pait": 0.0},
    "sanic": {"raw": 0.0, "use-pait": 0.0},
    "starlette": {"raw": 0.0, "use-pait": 0.0},
    "tornado": {"raw": 0.0, "use-pait": 0.0},
}


def run_and_calculate_time(func: Callable) -> float:
    total_duration = 0.0
    cnt: int = 100
    for _ in range(cnt):
        s_t = time.monotonic()
        func()
        total_duration += time.monotonic() - s_t
    return total_duration / cnt


def run_flask() -> None:
    @contextmanager
    def client_ctx() -> Generator[FlaskClient, None, None]:
        app: Flask = _flask.create_app()
        client: FlaskClient = app.test_client()
        client.get()
        # Establish an application context before running the tests.
        ctx: AppContext = app.app_context()
        ctx.push()
        yield client  # this is where the testing happens!
        ctx.pop()

    with client_ctx() as client:
        state_result["flask"]["raw"] = run_and_calculate_time(
            lambda: client.get(
                "/api/user-info?name=John&age=18&sex=man",
                headers={"token": "xxx"},
            )
        )

        state_result["flask"]["use-pait"] = run_and_calculate_time(
            lambda: client.get(
                "/api/user-info-by-pait?name=John&age=18&sex=man",
                headers={"token": "xxx"},
            )
        )


def run_sanic() -> None:
    logging.disable()  # don't know where to configure the log, the test environment will be canceled log
    app: _sanic.Sanic = _sanic.create_app()
    app.config.ACCESS_LOG = False
    state_result["sanic"]["raw"] = run_and_calculate_time(
        lambda: app.test_client.get(
            "/api/user-info?name=John&age=18&sex=man",
            headers={"token": "xxx"},
        )
    )
    state_result["sanic"]["use-pait"] = run_and_calculate_time(
        lambda: app.test_client.get(
            "/api/user-info-by-pait?name=John&age=18&sex=man",
            headers={"token": "xxx"},
        )
    )


def run_starlette() -> None:
    with TestClient(_starlette.create_app()) as client:
        state_result["starlette"]["raw"] = run_and_calculate_time(
            lambda: client.get(
                "/api/user-info?name=John&age=18&sex=man",
                headers={"token": "xxx"},
            )
        )
        state_result["starlette"]["use-pait"] = run_and_calculate_time(
            lambda: client.get(
                "/api/user-info-by-pait?name=John&age=18&sex=man",
                headers={"token": "xxx"},
            )
        )


def run_tornado() -> None:
    class BaseTestTornado(AsyncHTTPTestCase):
        def get_app(self) -> Application:
            return _tornado.create_app()

        def get_url(self, path: str) -> str:
            return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)

        def runTest(self) -> None:
            state_result["tornado"]["raw"] = run_and_calculate_time(
                lambda: self.fetch(
                    "/api/user-info?name=John&age=18&sex=man",
                    headers={"token": "xxx"},
                )
            )
            state_result["tornado"]["use-pait"] = run_and_calculate_time(
                lambda: self.fetch(
                    "/api/user-info-by-pait?name=John&age=18&sex=man",
                    headers={"token": "xxx"},
                )
            )

    BaseTestTornado().run()


if __name__ == "__main__":
    run_flask()
    run_starlette()
    run_tornado()
    run_sanic()

    for _, bucket in state_result.items():
        bucket["diff"] = bucket["use-pait"] - bucket["raw"]
    pprint(state_result)
