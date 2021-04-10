import asyncio
import sys
from tempfile import NamedTemporaryFile
from typing import Generator
from unittest import mock
import pytest

from sanic_testing import TestManager
from sanic_testing.testing import SanicTestClient
from pytest_mock import MockFixture

from example.param_verify.sanic_example import app, pait
from pait.app import auto_load_app
from pait.field import Body


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    TestManager(app)
    yield app.test_client


class TestSanic:
    def test_get(self, client: SanicTestClient) -> None:
        request, response = client.get("/api/get/3?uid=123&user_name=appl&sex=man")
        resp: dict = response.json

        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 3, "sex": "man"}

    def test_depend(self, client: SanicTestClient) -> None:
        request, response = client.post(
            "/api/depend?uid=123&user_name=appl",
            headers={"user-agent": "customer_agent"},
            json={"age": 2}
        )
        resp: dict = response.json
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self, client: SanicTestClient) -> None:
        request, response = client.get(
            "/api/cbv?uid=123&user_name=appl&age=2",
            headers={"user-agent": "customer_agent"}
        )
        resp: dict = response.json
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self, client: SanicTestClient) -> None:
        request, response = client.post(
            "/api/cbv",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        )
        resp: dict = response.json
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post(self, client: SanicTestClient) -> None:
        request, response = client.post(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        )
        resp: dict = response.json
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "content_type": "application/json"}

    def test_pait_model(self, client: SanicTestClient) -> None:
        request, response = client.post(
            "/api/pait_model?uid=123&user_name=appl",
            headers={"user-agent": "customer_agent"},
            json={"age": 2}
        )
        resp: dict = response.json
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_raise_tip(self, client: SanicTestClient) -> None:
        request, response = client.post(
            "/api/raise_tip",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        )
        resp: dict = response.json
        assert "exc" in resp

    def test_other_field(self, client: SanicTestClient) -> None:
        cookie_str: str = "abcd=abcd;"

        file_content: str = "Hello Word!"

        f = NamedTemporaryFile(delete=True)
        file_name: str = f.name
        f.write(file_content.encode())
        f.seek(0)

        request, response = client.post(
            "/api/other_field",
            headers={"cookie": cookie_str},
            data={"a": "1", "b": "2"},
            files={"upload_file": f}
        )
        resp: dict = response.json
        assert {
            "filename": file_name.split('/')[-1],
            "content": file_content,
            "form_a": "1",
            "form_b": "2",
            "cookie": {"abcd": "abcd"}
        } == resp["data"]

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import starlette
        with mock.patch.dict("sys.modules", sys.modules):
            assert starlette == auto_load_app.auto_load_app_class()

    # def test_lazy_property_raise_exc(self, client: SanicTestClient, mocker: MockFixture) -> None:
    #     future: asyncio.Future = asyncio.Future()
    #     future.set_exception(Exception("exc"))
    #     mocker.patch("pait.app.sanic.Request.json").return_value = future
    #
    #     @app.route("/api/lazy_property", methods=["POST"])
    #     @pait()
    #     async def demo(a: int = Body.i(), b: int = Body.i()) -> dict:
    #         return {}
    #
    #     with pytest.raises(Exception) as e:
    #         client.post("/api/lazy_property", json={"a": 1, "b": 2})
    #
    #     exec_msg = e.value.args[0]
    #     assert exec_msg == "exc"
