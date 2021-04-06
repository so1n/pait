from typing import Generator
from flask.ctx import AppContext
from flask.testing import FlaskClient
import pytest

from example.param_verify.flask_example import app


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


class TestFlask:
    def test_get(self, client: FlaskClient) -> None:
        resp: dict = client.get("/api/get/3?uid=123&user_name=appl&sex=man").get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 3, "sex": "man"}

    def test_depend(self, client: FlaskClient) -> None:
        resp: dict = client.get(
            "/api/depend?uid=123&user_name=appl&age=2",
            headers={"user-agent": "customer_agent"}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self, client: FlaskClient) -> None:
        resp: dict = client.get(
            "/api/cbv?uid=123&user_name=appl&age=2",
            headers={"user-agent": "customer_agent"}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/cbv",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post_post(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).get_json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "content_type": "application/json"}

    def test_raise_tip(self, client: FlaskClient) -> None:
        resp: dict = client.post(
            "/api/raise_tip",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).get_json()
        assert "exc" in resp


