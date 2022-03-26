import difflib
import sys
from tempfile import NamedTemporaryFile
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from flask import Flask, Response
from flask.ctx import AppContext
from flask.testing import FlaskClient
from pytest_mock import MockFixture

from example.param_verify import flask_example
from pait.api_doc.html import get_redoc_html, get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import auto_load_app
from pait.app.flask import FlaskTestHelper, load_app
from pait.model import response
from tests.conftest import enable_mock


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = flask_example.create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


def response_test_helper(
    client: FlaskClient, route_handler: Callable, pait_response: Type[response.PaitBaseResponseModel]
) -> None:
    from pait.app.flask.plugin.mock_response import MockPlugin

    test_helper: FlaskTestHelper = FlaskTestHelper(client, route_handler)
    test_helper.get()

    with enable_mock(route_handler, MockPlugin):
        resp: Response = test_helper.get()
        for key, value in pait_response.header.items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
            pait_response, response.PaitTextResponseModel
        ):
            assert resp.get_data().decode() == pait_response.get_example_value()
        else:
            assert resp.get_data() == pait_response.get_example_value()


class TestFlask:
    def test_raise_tip_route(self, client: FlaskClient) -> None:
        msg: str = FlaskTestHelper(client, flask_example.raise_tip_route, header_dict={"Content-Type": "test"}).json()[
            "msg"
        ]
        assert msg == "error param:content__type, Can not found content__type value"

    def test_post(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            flask_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            flask_test_helper.json(),
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

    def test_check_json_route(self, client: FlaskClient) -> None:
        for url, api_code in [
            (
                "/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url).get_json()
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_auto_complete_json_route(self, client: FlaskClient) -> None:
        def check_dict(source_dict: dict, target_dict: dict) -> None:
            for key, value in source_dict.items():
                if isinstance(value, dict) and key in target_dict:
                    return check_dict(value, target_dict[key])
                else:
                    if key not in target_dict or not isinstance(value, type(target_dict[key])):
                        raise RuntimeError("check error")

        auto_complete_dict: dict = client.get(
            "/api/auto-complete-json-plugin?uid=123&user_name=appl&sex=man&age=10"
        ).get_json()
        real_dict: dict = client.get(
            "/api/auto-complete-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1"
        ).get_json()
        check_dict(auto_complete_dict, real_dict)

    def test_depend_route(self, client: FlaskClient) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == FlaskTestHelper(
            client,
            flask_example.depend_route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def test_same_alias_name(self, client: FlaskClient) -> None:
        assert (
            FlaskTestHelper(
                client,
                flask_example.same_alias_route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            FlaskTestHelper(
                client,
                flask_example.same_alias_route,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def test_field_default_factory_route(self, client: FlaskClient) -> None:
        assert (
            FlaskTestHelper(
                client,
                flask_example.field_default_factory_route,
                body_dict={"demo_value": 0},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"demo_value": 0, "data_list": [], "data_dict": {}}}
        )

    def test_pait_base_field_route(self, client: FlaskClient) -> None:
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
                    "filename": f1.name,
                    "form_a": "1",
                    "form_b": "2",
                    "form_c": ["3", "4"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == FlaskTestHelper(
                client,
                flask_example.pait_base_field_route,
                file_dict={"upload_file": f1},
                cookie_dict={"abcd": "abcd"},
                form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def test_check_param(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in flask_test_helper.json()["msg"]
        flask_test_helper = FlaskTestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert "birthday requires param alias_user_name, which if not none" in flask_test_helper.json()["msg"]
        flask_test_helper = FlaskTestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert flask_test_helper.json()["code"] == 0

    def test_check_response(self, client: FlaskClient) -> None:
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            flask_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            flask_test_helper.json()
        flask_test_helper = FlaskTestHelper(
            client,
            flask_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        flask_test_helper.json()

    def test_mock_route(self, client: FlaskClient) -> None:
        assert (
            FlaskTestHelper(
                client,
                flask_example.mock_route,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == flask_example.UserSuccessRespModel2.get_example_value()
        )

    def test_pait_model(self, client: FlaskClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {
                "uid": 123,
                "user_agent": "customer_agent",
                "user_info": {"age": 2, "user_name": "appl"},
            },
        } == FlaskTestHelper(
            client,
            flask_example.pait_model_route,
            header_dict={"user-agent": "customer_agent"},
            query_dict={"uid": 123, "user_name": "appl"},
            body_dict={"user_info": {"age": 2, "user_name": "appl"}},
            strict_inspection_check_json_content=False,
        ).json()

    def test_depend_contextmanager(self, client: FlaskClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            flask_example.depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        flask_test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        flask_test_helper = FlaskTestHelper(
            client,
            flask_example.depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        flask_test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_pre_depend_contextmanager(self, client: FlaskClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        flask_test_helper: FlaskTestHelper = FlaskTestHelper(
            client,
            flask_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        flask_test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        flask_test_helper = FlaskTestHelper(
            client,
            flask_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        flask_test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_get_cbv(self, client: FlaskClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == FlaskTestHelper(
            client,
            flask_example.CbvRoute.get,
            query_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_post_cbv(self, client: FlaskClient) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == FlaskTestHelper(
            client,
            flask_example.CbvRoute.post,
            body_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def test_text_response(self, client: FlaskClient) -> None:
        response_test_helper(client, flask_example.text_response_route, response.PaitTextResponseModel)

    def test_html_response(self, client: FlaskClient) -> None:
        response_test_helper(client, flask_example.html_response_route, response.PaitHtmlResponseModel)

    def test_file_response(self, client: FlaskClient) -> None:
        response_test_helper(client, flask_example.file_response_route, response.PaitFileResponseModel)

    def test_test_helper_not_support_mutil_method(self, client: FlaskClient) -> None:
        client.application.add_url_rule(
            "/api/text-resp", view_func=flask_example.text_response_route, methods=["GET", "POST"]
        )
        with pytest.raises(RuntimeError) as e:
            FlaskTestHelper(client, flask_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self, client: FlaskClient) -> None:
        assert client.get("/swagger").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/swagger?pin_code=6666").get_data().decode() == get_swagger_ui_html(
            "http://localhost/openapi.json?pin_code=6666", "Pait Doc"
        )
        assert client.get("/redoc?pin_code=6666").get_data().decode() == get_redoc_html(
            "http://localhost/openapi.json?pin_code=6666", "Pait Doc"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(client.get("/openapi.json?pin_code=6666").json),
                str(
                    PaitOpenAPI(
                        load_app(client.application),
                        title="Pait Doc",
                        open_api_server_list=[{"url": "http://localhost", "description": ""}],
                    ).open_api_dict
                ),
            ).quick_ratio()
            > 0.95
        )

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import flask

        with mock.patch.dict("sys.modules", sys.modules):
            assert flask == auto_load_app.auto_load_app_class()
