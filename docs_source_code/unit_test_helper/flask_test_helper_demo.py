# flake8: noqa: E402
from typing import Type

from flask import Flask, Response, jsonify
from pydantic import BaseModel, Field

from pait.app.flask import pait
from pait.field import Body
from pait.model.response import JsonResponseModel


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
    return_error_resp: bool = Body.i(description="return error resp", default=False),
) -> Response:
    if return_error_resp:
        return jsonify()
    return jsonify({"uid": uid, "user_name": username, "a": 123})


app = Flask("demo")
app.add_url_rule("/api", "demo", demo_post, methods=["POST"])

from pait.extra.config import apply_block_http_method_set

###########################################################
# Block the OPTIONS method that Flask automatically adds  #
###########################################################
from pait.g import config

config.init_config(apply_func_list=[apply_block_http_method_set({"OPTIONS"})])


#############
# unit test #
#############
from typing import Generator

import pytest
from flask.ctx import AppContext
from flask.testing import FlaskClient

from pait.app.flask import FlaskTestHelper


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


def test_demo_post_route_by_call_json(client: FlaskClient) -> None:
    test_helper = FlaskTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_use_method(client: FlaskClient) -> None:
    test_helper = FlaskTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    assert test_helper.json(method="POST") == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_raw_web_framework_response(client: FlaskClient) -> None:
    test_helper = FlaskTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test"},
    )
    resp = test_helper.post()
    assert resp.status_code == 200
    assert resp.json == {"uid": 11, "user_name": "test"}


def test_demo_post_route_by_test_helper_check_response_error(client: FlaskClient) -> None:
    test_helper = FlaskTestHelper(
        client=client,
        func=demo_post,
        body_dict={"uid": 11, "username": "test", "return_error_resp": True},
    )
    assert test_helper.json() == {"uid": 11, "user_name": "test"}
