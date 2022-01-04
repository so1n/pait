import asyncio
import sys
from tempfile import NamedTemporaryFile
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from pytest_mock import MockFixture
from requests import Response  # type: ignore
from starlette.testclient import TestClient

from example.param_verify import starlette_example
from pait.app import auto_load_app
from pait.app.starlette import StarletteTestHelper
from pait.model import response
from tests.conftest import enable_mock


@pytest.fixture
def client(mocker: MockFixture) -> Generator[TestClient, None, None]:
    # fix staelette.testclient get_event_loop status is close
    def get_event_loop() -> asyncio.AbstractEventLoop:
        try:
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    mocker.patch("asyncio.get_event_loop").return_value = get_event_loop()
    client: TestClient = TestClient(starlette_example.create_app())
    yield client


def response_test_helper(
    client: TestClient, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
) -> None:
    test_helper: StarletteTestHelper = StarletteTestHelper(client, route_handler)
    test_helper.get()

    with enable_mock(test_helper):
        resp: Response = test_helper.get()
        for key, value in pait_response.header.items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
            pait_response, response.PaitTextResponseModel
        ):
            assert resp.text == pait_response.get_example_value()
        else:
            assert resp.content == pait_response.get_example_value()


class TestStarlette:
    def test_raise_tip_route(self, client: TestClient) -> None:
        assert {
            "code": -1,
            "msg": (
                'File "/home/so1n/github/pait/example/param_verify/starlette_example.py", '
                "line 46, "
                "in raise_tip_route. error:content__type value is <class 'pydantic.fields.UndefinedType'>"
            ),
        } == StarletteTestHelper(client, starlette_example.raise_tip_route, header_dict={"Content-Type": "test"}).json()

    def test_post(self, client: TestClient) -> None:
        test_helper: StarletteTestHelper = StarletteTestHelper(
            client,
            starlette_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
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

    def test_depend_route(self, client: TestClient) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == StarletteTestHelper(
            client,
            starlette_example.depend_route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def test_same_alias_name(self, client: TestClient) -> None:
        assert (
            StarletteTestHelper(
                client,
                starlette_example.same_alias_route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            StarletteTestHelper(
                client,
                starlette_example.same_alias_route,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def test_pait_base_field_route(self, client: TestClient) -> None:
        file_content: str = "Hello Word!"

        with NamedTemporaryFile(delete=True) as f1:
            f1.write(file_content.encode())
            f1.seek(0)
            assert {
                "code": 0,
                "data": {
                    "age": 2,
                    "content": "Hello Word!",
                    "cookie": {"abcd": "abcd"},
                    "email": "example@xxx.com",
                    "filename": f1.name.split("/")[-1],
                    "form_a": "1",
                    "form_b": "2",
                    "form_c": ["3", "4"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == StarletteTestHelper(
                client,
                starlette_example.pait_base_field_route,
                file_dict={"upload_file": f1},
                form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                cookie_dict={"cookie": "abcd=abcd;"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import starlette

        with mock.patch.dict("sys.modules", sys.modules):
            assert starlette == auto_load_app.auto_load_app_class()
