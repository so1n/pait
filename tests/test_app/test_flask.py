import sys
from tempfile import NamedTemporaryFile
from typing import Generator, List
from unittest import mock

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from pytest_mock import MockFixture

from example.param_verify.flask_example import create_app
from example.param_verify.flask_example import test_check_param as check_param_route
from example.param_verify.flask_example import test_check_response as check_resp_route
from example.param_verify.flask_example import test_depend_contextmanager as depend_contextmanager
from example.param_verify.flask_example import test_other_field as other_field_route
from example.param_verify.flask_example import test_pait as pait_route
from example.param_verify.flask_example import test_post as post_route
from pait.app import auto_load_app
from pait.app.flask import FlaskTestHelper
from pait.g import config


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@pytest.fixture
def enable_mock_response() -> Generator[None, None, None]:
    config.enable_mock_response = True
    yield None
    config.enable_mock_response = False


class TestFlask:
    def test_get(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            pait_route,
            path_dict={"age": 3},
            query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
        )
        resp_list: List[dict] = [
            client.get("/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg").get_json(),
            flask_test_helper.get().get_json(),
        ]
        for resp in resp_list:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "email": "example@xxx.com",
                "age": 3,
                "sex": "man",
                "multi_user_name": ["abc", "efg"],
            }

    def test_check_response(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            check_resp_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            flask_test_helper.get().get_json()
        flask_test_helper = FlaskTestHelper(
            client,
            check_resp_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        flask_test_helper.get().get_json()

    def test_check_param(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert "requires at most one of param user_name or alias_user_name" in flask_test_helper.get().get_json()["msg"]
        flask_test_helper = FlaskTestHelper(
            client, check_param_route, query_dict={"uid": 123, "sex": "man", "age": 10, "alias_user_name": "appe"}
        )
        assert "birthday requires param alias_user_name, which if not none" in flask_test_helper.get().get_json()["msg"]

    def test_depend_contextmanager(self, client: FlaskClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            depend_contextmanager,
            query_dict={"uid": 123},
        )
        flask_test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        flask_test_helper = FlaskTestHelper(
            client,
            depend_contextmanager,
            query_dict={"uid": 123, "is_raise": True},
        )
        flask_test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_mock_get(self, client: FlaskClient) -> None:
        config.enable_mock_response = True
        resp: dict = client.get(
            "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
        ).get_json()
        assert resp == {
            "code": 0,
            "data": {
                "age": 99,
                "email": "example@so1n.me",
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
            },
            "msg": "success",
        }
        config.enable_mock_response = False

    def test_depend(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/depend?uid=123&user_name=appl", headers={"user-agent": "customer_agent"}, json={"age": 2}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self, client: FlaskClient) -> None:
        resp: dict = client.get(
            "/api/cbv?uid=123&user_name=appl&age=2", headers={"user-agent": "customer_agent"}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/cbv", headers={"user-agent": "customer_agent"}, json={"uid": 123, "user_name": "appl", "age": 2}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            flask_test_helper.post().get_json(),
            client.post(
                "/api/post",
                headers={"user-agent": "customer_agent"},
                json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            ).get_json(),
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
            }

    def test_pait_model(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/pait_model?uid=123&user_name=appl", headers={"user-agent": "customer_agent"}, json={"age": 2}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_raise_tip(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/raise_tip", headers={"user-agent": "customer_agent"}, json={"uid": 123, "user_name": "appl", "age": 2}
        ).get_json()
        assert "msg" in resp

    def test_other_field(self, client: FlaskClient) -> None:

        file_content: str = "Hello Word!"

        f1 = NamedTemporaryFile(delete=True)
        file_name: str = f1.name
        f1.write(file_content.encode())
        f1.seek(0)
        f2 = NamedTemporaryFile(delete=True)
        f2.name = file_name  # type: ignore
        f2.write(file_content.encode())
        f2.seek(0)

        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client, other_field_route, file_dict={"upload_file": f1}, form_dict={"a": "1", "b": "2", "c": "3"}
        )

        client.set_cookie("localhost", "abcd", "abcd")
        for resp in [
            flask_test_helper.post().get_json(),
            client.post("/api/other_field", data={"a": "1", "b": "2", "upload_file": f2, "c": "3"}).get_json(),
        ]:
            assert {
                "filename": file_name,
                "content": file_content,
                "form_a": "1",
                "form_b": "2",
                "form_c": ["3"],
                "cookie": {"abcd": "abcd"},
            } == resp["data"]

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import flask

        with mock.patch.dict("sys.modules", sys.modules):
            assert flask == auto_load_app.auto_load_app_class()
