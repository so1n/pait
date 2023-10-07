# flake8: noqa: E402
from typing import Type

from pydantic import BaseModel, Field
from sanic.app import Sanic
from sanic.response import HTTPResponse, json

from pait.app.sanic import pait
from pait.field import Body
from pait.model.response import JsonResponseModel


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
async def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
    return_error_resp: bool = Body.i(description="return error resp", default=False),
) -> HTTPResponse:
    if return_error_resp:
        return json({})
    return json({"uid": uid, "user_name": username})


app = Sanic(name="demo")
app.add_route(demo_post, "/api", methods=["POST"])


from typing import Generator

#############
# unit test #
#############
import pytest
from sanic_testing.testing import SanicTestClient

from pait.app.sanic import SanicTestHelper


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    yield app.test_client


def test_demo_post_route_by_call_json(client: SanicTestClient) -> None:
    test_helper = SanicTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_use_method(client: SanicTestClient) -> None:
    test_helper = SanicTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json(method="POST") == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_raw_web_framework_response(client: SanicTestClient) -> None:
    test_helper = SanicTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    resp = test_helper.post()
    assert resp.status_code == 200
    assert resp.json == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_test_helper_check_response_error(client: SanicTestClient) -> None:
    test_helper = SanicTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test", "return_error_resp": True},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}
