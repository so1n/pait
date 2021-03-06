import asyncio
import sys
from tempfile import NamedTemporaryFile
from typing import Generator
from unittest import mock

import pytest
from pytest_mock import MockFixture
from requests import Response
from starlette.testclient import TestClient

from example.param_verify.starlette_example import create_app
from example.param_verify.starlette_example import test_check_param as check_param_route
from example.param_verify.starlette_example import test_get as get_route
from example.param_verify.starlette_example import test_other_field as other_field_route
from example.param_verify.starlette_example import test_post as post_route
from pait.app import auto_load_app
from pait.app.starlette import StarletteTestHelper
from pait.g import config


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
        test_helper: StarletteTestHelper[Response] = StarletteTestHelper(
            client,
            get_route,
            path_dict={"age": 3},
            query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
        )
        for resp in [
            test_helper.get().json(),
            client.get("/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg").json(),
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "email": "example@xxx.com",
                "age": 3,
                "sex": "man",
                "multi_user_name": ["abc", "efg"],
            }

    def test_check_param(self, client: TestClient) -> None:
        startlette_test_helper: StarletteTestHelper[Response] = StarletteTestHelper(
            client,
            check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert (
            "requires at most one of param user_name or alias_user_name" in startlette_test_helper.get().json()["exc"]
        )
        startlette_test_helper = StarletteTestHelper(
            client, check_param_route, query_dict={"uid": 123, "sex": "man", "age": 10, "alias_user_name": "appe"}
        )
        assert (
            "error:birthday requires param alias_user_name, which if not none"
            in startlette_test_helper.get().json()["exc"]
        )

    def test_mock_get(self, client: TestClient) -> None:
        config.enable_mock_response = True
        resp: dict = client.get(
            "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
        ).json()
        assert resp == {
            "code": 0,
            "data": {"age": 99, "email": "example@so1n.me", "uid": 6666666666, "user_name": "mock_name"},
            "msg": "success",
        }
        config.enable_mock_response = False

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
        test_helper: StarletteTestHelper[Response] = StarletteTestHelper(
            client,
            post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.post().json(),
            client.post(
                "/api/post",
                headers={"user-agent": "customer_agent"},
                json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            ).json(),
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
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

        f1 = NamedTemporaryFile(delete=True)
        file_name: str = f1.name
        f1.write(file_content.encode())
        f1.seek(0)
        f2 = NamedTemporaryFile(delete=True)
        f2.name = file_name  # type: ignore
        f2.write(file_content.encode())
        f2.seek(0)

        test_helper: StarletteTestHelper[Response] = StarletteTestHelper(
            client,
            other_field_route,
            cookie_dict={"cookie": cookie_str},
            file_dict={"upload_file": f1},
            form_dict={"a": "1", "b": "2", "c": ["3"]},
        )
        for resp in [
            test_helper.post().json(),
            client.post(
                "/api/other_field",
                data={"a": "1", "b": "2", "c": ["3"]},
                headers={"cookie": cookie_str},
                files={"upload_file": f2},
            ).json(),
        ]:
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
