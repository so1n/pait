from typing import Generator, Tuple, Type

import pytest
from flask import Flask, Response, make_response
from flask.ctx import AppContext
from flask.json import jsonify
from flask.testing import FlaskClient
from pydantic import BaseModel, Field

from example.flask_example import main_example
from pait.app.base import CheckResponseException
from pait.app.flask import FlaskTestHelper, pait
from pait.model import response


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = main_example.create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


class TestPaitTestHelper:
    def test_not_found_call_id(self, client: FlaskClient) -> None:
        def demo() -> None:
            pass

        with pytest.raises(RuntimeError) as e:
            FlaskTestHelper(client, demo)

        exec_msg: str = e.value.args[0]
        assert "Can not found pait id from" in exec_msg

    def test_response_model_list_is_empty(self, client: FlaskClient) -> None:
        @pait()
        def demo() -> Response:
            return make_response("", 400)

        client.application.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
        assert FlaskTestHelper(client, demo).get().status_code == 400

    def test_check_diff_resp_dict(self, client: FlaskClient) -> None:
        class DemoResponse(response.JsonResponseModel):
            class DataModel(BaseModel):
                a: str

            response_data: Type[BaseModel] = DataModel

        @pait(response_model_list=[DemoResponse])
        def demo() -> Response:
            return jsonify({"a": "a", "b": "b"})

        client.application.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
        with pytest.raises(CheckResponseException) as e:
            FlaskTestHelper(client, demo).get()

        exec_msg: str = e.value.args[0]
        assert "check json content error, exec: Can not found key from model" in exec_msg

    def test_error_response(self, client: FlaskClient) -> None:
        class DemoResponse(response.BaseResponseModel):
            media_type = response.JsonResponseModel.media_type
            status_code = response.JsonResponseModel.status_code

        @pait(response_model_list=[DemoResponse])
        def demo() -> Response:
            return jsonify({"a": "a", "b": "b"})

        client.application.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
        with pytest.raises(TypeError) as e:
            FlaskTestHelper(client, demo).get()

        exec_msg: str = e.value.args[0]
        assert "Pait not support response model" in exec_msg

    def test_status_code_and_media_type_and_header_error(self, client: FlaskClient) -> None:
        class DemoResponse(response.TextResponseModel):
            status_code: Tuple[int] = (999,)

            class HeaderModel(BaseModel):
                faker_header: str = Field(default="", alias="faker-header")

            header = HeaderModel

        @pait(response_model_list=[DemoResponse])
        def demo() -> Response:
            return make_response("")

        client.application.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
        with pytest.raises(CheckResponseException) as e:
            FlaskTestHelper(client, demo).get()

        exec_msg: str = e.value.args[0]
        for i in [
            "check status code error",
            "check media type error",
            "check header error",
        ]:
            assert i in exec_msg

    def test_http_method_call(self, client: FlaskClient) -> None:
        for http_method in ["get", "head"]:
            getattr(FlaskTestHelper(client, main_example.html_response_route), http_method)()

        for http_method in ["patch", "post", "put", "delete"]:
            with pytest.raises(CheckResponseException) as e:
                http_method, getattr(FlaskTestHelper(client, main_example.html_response_route), http_method)()

            assert e.value.status_code == 405
