import asyncio
import sys
from tempfile import NamedTemporaryFile
from typing import Generator
from unittest import mock

import pytest
from pytest_mock import MockFixture
from starlette.testclient import TestClient

from example.param_verify.starlette_example import create_app
from pait.app import auto_load_app


@pytest.fixture
def client(mocker: MockFixture) -> Generator[TestClient, None, None]:
    # fix staelette.testclient get_event_loop status is close
    def get_event_loop() -> asyncio.AbstractEventLoop:
        try:
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    mocker.patch("asyncio.get_event_loop").return_value = get_event_loop()
    client: TestClient = TestClient(create_app())
    yield client


class TestStarlette:
    def test_get(self, client: TestClient) -> None:
        resp: dict = client.get(
            "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {
            "uid": 123,
            "user_name": "appl",
            "email": "example@xxx.com",
            "age": 3,
            "sex": "man",
            "multi_user_name": ["abc", "efg"],
        }

    def test_depend(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/depend?uid=123&user_name=appl", headers={"user-agent": "customer_agent"}, json={"age": 2}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self, client: TestClient) -> None:
        resp: dict = client.get(
            "/api/cbv?uid=123&user_name=appl&age=2", headers={"user-agent": "customer_agent"}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/cbv", headers={"user-agent": "customer_agent"}, json={"uid": 123, "user_name": "appl", "age": 2}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {
            "uid": 123, "user_name": "appl", "age": 2, "content_type": "application/json", "sex": "man"
        }

    def test_pait_model(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/pait_model?uid=123&user_name=appl", headers={"user-agent": "customer_agent"}, json={"age": 2}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_raise_tip(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/raise_tip", headers={"user-agent": "customer_agent"}, json={"uid": 123, "user_name": "appl", "age": 2}
        ).json()
        assert "exc" in resp

    def test_other_field(self, client: TestClient) -> None:
        cookie_str: str = "abcd=abcd;"

        file_content: str = "Hello Word!"

        f = NamedTemporaryFile(delete=True)
        file_name: str = f.name
        f.write(file_content.encode())
        f.seek(0)

        form_dict: dict = {"a": "1", "b": "2", "c": "3", "upload_file": f}
        resp: dict = client.post("/api/other_field", headers={"cookie": cookie_str}, files=form_dict).json()
        assert {
            "filename": file_name.split("/")[-1],
            "content": file_content,
            "form_a": "1",
            "form_b": "2",
            "form_c": ["3"],
            "cookie": {"abcd": "abcd"},
        } == resp["data"]

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import starlette

        with mock.patch.dict("sys.modules", sys.modules):
            assert starlette == auto_load_app.auto_load_app_class()
