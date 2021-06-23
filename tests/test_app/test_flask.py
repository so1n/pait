import sys
from tempfile import NamedTemporaryFile
from typing import Generator
from unittest import mock

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient

from example.param_verify.flask_example import create_app
from pait.app import auto_load_app


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


class TestFlask:
    def test_get(self, client: FlaskClient) -> None:
        resp: dict = client.get(
            "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {
            "uid": 123,
            "user_name": "appl",
            "email": "example@xxx.com",
            "age": 3,
            "sex": "man",
            "multi_user_name": ["abc", "efg"],
        }

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
        resp: dict = client.post(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {
            "uid": 123, "user_name": "appl", "age": 2, "content_type": "application/json", "sex": "man"
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
        assert "exc" in resp

    def test_other_field(self, client: FlaskClient) -> None:

        file_content: str = "Hello Word!"

        f = NamedTemporaryFile(delete=True)
        file_name: str = f.name
        f.write(file_content.encode())
        f.seek(0)

        form_dict: dict = {"a": "1", "b": "2", "upload_file": f, "c": "3"}
        client.set_cookie("localhost", "abcd", "abcd")
        resp: dict = client.post("/api/other_field", data=form_dict).get_json()
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
