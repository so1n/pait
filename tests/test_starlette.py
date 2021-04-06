from typing import Generator
import pytest

from starlette.testclient import TestClient

from example.param_verify.starlette_example import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    client: TestClient = TestClient(app)
    yield client


class TestStarlette:
    def test_get(self, client: TestClient) -> None:
        resp: dict = client.get("/api/get/3?uid=123&user_name=appl&sex=man").json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 3, "sex": "man"}

    def test_depend(self, client: TestClient) -> None:
        resp: dict = client.get(
            "/api/depend?uid=123&user_name=appl&age=2",
            headers={"user-agent": "customer_agent"}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self, client: TestClient) -> None:
        resp: dict = client.get(
            "/api/cbv?uid=123&user_name=appl&age=2",
            headers={"user-agent": "customer_agent"}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/cbv",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post_post(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).json()
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "content_type": "application/json"}

    def test_raise_tip(self, client: TestClient) -> None:
        resp: dict = client.post(
            "/api/raise_tip",
            headers={"user-agent": "customer_agent"},
            json={"uid": 123, "user_name": "appl", "age": 2}
        ).json()
        assert "exc" in resp

