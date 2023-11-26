# flake8: noqa: E402
from typing import Type

from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Json
from pait.model.response import JsonResponseModel


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
async def demo_post(
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
    return_error_resp: bool = Json.i(description="return error resp", default=False),
) -> JSONResponse:
    if return_error_resp:
        return JSONResponse({})
    return JSONResponse({"uid": uid, "user_name": username})


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])


from typing import Generator

#############
# unit test #
#############
import pytest
from starlette.testclient import TestClient

from pait.app.starlette import StarletteTestHelper


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


def test_demo_post_route_by_call_json(client: TestClient) -> None:
    test_helper = StarletteTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_use_method(client: TestClient) -> None:
    test_helper = StarletteTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json(method="POST") == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_raw_web_framework_response(client: TestClient) -> None:
    test_helper = StarletteTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    resp = test_helper.post()
    assert resp.status_code == 200
    assert resp.json() == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_test_helper_check_response_error(client: TestClient) -> None:
    test_helper = StarletteTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test", "return_error_resp": True},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}
