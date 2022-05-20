import difflib
import json
import random
import sys
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable, Generator, Type
from unittest import mock

import pytest
from flask import Flask, Response
from flask.ctx import AppContext
from flask.testing import FlaskClient
from pytest_mock import MockFixture

from example.param_verify import flask_example
from pait.api_doc.html import get_redoc_html, get_swagger_ui_html
from pait.api_doc.open_api import PaitOpenAPI
from pait.app import auto_load_app, get_app_attribute, set_app_attribute
from pait.app.flask import TestHelper as _TestHelper
from pait.app.flask import load_app
from pait.model import response
from tests.conftest import enable_plugin, grpc_test_create_user_request, grpc_test_openapi

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


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

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, MockPlugin.build()):
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
        msg: str = _TestHelper(client, flask_example.raise_tip_route, header_dict={"Content-Type": "test"}).json()[
            "msg"
        ]
        assert msg == "error param:content__type, Can not found content__type value"

    def test_post(self, client: FlaskClient) -> None:
        flask_test_helper: _TestHelper = _TestHelper(
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
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            flask_example.auto_complete_json_route,
        )
        resp_dict: dict = flask_test_helper.json()
        assert resp_dict["data"]["uid"] == 100
        assert resp_dict["data"]["music_list"][1]["name"] == ""
        assert resp_dict["data"]["music_list"][1]["singer"] == ""

    def test_depend_route(self, client: FlaskClient) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == _TestHelper(
            client,
            flask_example.depend_route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def test_same_alias_name(self, client: FlaskClient) -> None:
        assert (
            _TestHelper(
                client,
                flask_example.same_alias_route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            _TestHelper(
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
            _TestHelper(
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
            } == _TestHelper(
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
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in flask_test_helper.json()["msg"]
        flask_test_helper = _TestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert "birthday requires param alias_user_name, which if not none" in flask_test_helper.json()["msg"]
        flask_test_helper = _TestHelper(
            client,
            flask_example.check_param_route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert flask_test_helper.json()["code"] == 0

    def test_check_response(self, client: FlaskClient) -> None:
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            flask_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            flask_test_helper.json()
        flask_test_helper = _TestHelper(
            client,
            flask_example.check_response_route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        flask_test_helper.json()

    def test_mock_route(self, client: FlaskClient) -> None:
        assert (
            _TestHelper(
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
        } == _TestHelper(
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
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            flask_example.depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        flask_test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        flask_test_helper = _TestHelper(
            client,
            flask_example.depend_contextmanager_route,
            query_dict={"uid": 123, "is_raise": True},
        )
        flask_test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_pre_depend_contextmanager(self, client: FlaskClient, mocker: MockFixture) -> None:
        error_logger = mocker.patch("example.param_verify.model.logging.error")
        info_logger = mocker.patch("example.param_verify.model.logging.info")
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            flask_example.pre_depend_contextmanager_route,
            query_dict={"uid": 123},
        )
        flask_test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        flask_test_helper = _TestHelper(
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
        } == _TestHelper(
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
        } == _TestHelper(
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
            _TestHelper(client, flask_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self, client: FlaskClient) -> None:
        flask_example.add_api_doc_route(client.application)
        assert client.get("/swagger").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/swagger?pin_code=6666").get_data().decode() == get_swagger_ui_html(
            "http://localhost/openapi.json?pin_code=6666", "Pait Api Doc(private)"
        )
        assert client.get("/redoc?pin_code=6666").get_data().decode() == get_redoc_html(
            "http://localhost/openapi.json?pin_code=6666", "Pait Api Doc(private)"
        )
        assert (
            json.loads(client.get("/openapi.json?pin_code=6666&template-token=xxx").get_data().decode())["paths"][
                "/api/user"
            ]["get"]["parameters"][0]["schema"]["example"]
            == "xxx"
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

    def test_cache_response(self, client: FlaskClient) -> None:
        def del_key(key: str) -> None:
            redis: flask_example.Redis = flask_example.Redis()
            for _key in redis.scan_iter(match=key + "*"):
                redis.delete(_key)

        # test not exc
        del_key("cache_response")
        result1: str = _TestHelper(client, flask_example.cache_response).get().get_data()
        result2: str = _TestHelper(client, flask_example.cache_response).get().get_data()
        result3: str = _TestHelper(client, flask_example.cache_response1).get().get_data()
        result4: str = _TestHelper(client, flask_example.cache_response1).get().get_data()
        assert result1 == result2
        assert result3 == result4
        assert result1 != result3
        assert result2 != result4
        del_key("cache_response")
        assert result1 != _TestHelper(client, flask_example.cache_response).get().get_data()
        assert result3 != _TestHelper(client, flask_example.cache_response1).get().get_data()

        # test not include exc
        del_key("cache_response")
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, flask_example.cache_response, query_dict={"raise_exc": 1}).get().get_data()

        exec_msg: str = e.value.args[0]
        assert "'status_code': 500" in exec_msg

        # test include exc
        del_key("cache_response")
        result_5 = _TestHelper(client, flask_example.cache_response, query_dict={"raise_exc": 2}).get().get_data()
        result_6 = _TestHelper(client, flask_example.cache_response, query_dict={"raise_exc": 2}).get().get_data()
        assert result_5 == result_6

    def test_cache_other_response_type(self, client: FlaskClient) -> None:
        def _handler(_route_handler: Callable) -> Any:
            pait_core_model: "PaitCoreModel" = getattr(_route_handler, "pait_core_model")
            pait_response: Type[response.PaitBaseResponseModel] = pait_core_model.response_model_list[0]
            resp: Response = _TestHelper(client, _route_handler).get()
            if issubclass(pait_response, response.PaitHtmlResponseModel) or issubclass(
                pait_response, response.PaitTextResponseModel
            ):
                return resp.get_data().decode()
            else:
                return resp.get_data()

        key: str = "test_cache_other_response_type"

        redis: flask_example.Redis = flask_example.Redis(decode_responses=True)
        for route_handler in [flask_example.text_response_route, flask_example.html_response_route]:
            redis.delete(key)
            with enable_plugin(
                route_handler, flask_example.CacheResponsePlugin.build(redis=redis, name=key, cache_time=5)
            ):
                assert _handler(route_handler) == _handler(route_handler)

    def test_cache_response_param_name(self, client: FlaskClient) -> None:
        key: str = "test_cache_response_param_name"
        redis: flask_example.Redis = flask_example.Redis(decode_responses=True)
        route_handler: Callable = flask_example.post_route

        for _key in redis.scan_iter(match=key + "*"):
            redis.delete(_key)
        with enable_plugin(
            route_handler,
            flask_example.CacheResponsePlugin.build(
                redis=redis, name=key, enable_cache_name_merge_param=True, cache_time=5
            ),
        ):
            test_helper1: _TestHelper = _TestHelper(
                client,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )
            test_helper2: _TestHelper = _TestHelper(
                client,
                route_handler,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "woman"},
            )
            assert test_helper1.json() == test_helper1.json()
            assert test_helper2.json() == test_helper2.json()
            assert test_helper1.json() != test_helper2.json()

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import flask

        with mock.patch.dict("sys.modules", sys.modules):
            assert flask == auto_load_app.auto_load_app_class()

    def test_app_attribute(self, client: FlaskClient) -> None:
        key: str = "app_test_app_attribute"
        value: int = random.randint(1, 100)
        set_app_attribute(client.application, key, value)

        is_call: bool = False

        def demo_route() -> None:
            assert get_app_attribute(client.application, key) == value
            nonlocal is_call
            is_call = True

        url: str = "/api/test-invoke-demo"
        client.application.add_url_rule(url, view_func=demo_route)
        client.get(url)
        assert is_call


class TestFlaskGrpc:
    def test_create_user(self, client: FlaskClient) -> None:
        flask_example.add_grpc_gateway_route(client.application)
        flask_example.add_api_doc_route(client.application)

        def _(request_dict: dict) -> None:
            body: bytes = client.post("/api/user/create", json=request_dict).data
            assert body == b"{}\n"

        grpc_test_create_user_request(client.application, _)

    def test_grpc_openapi(self, client: FlaskClient) -> None:
        flask_example.add_grpc_gateway_route(client.application)

        from pait.app.flask import load_app

        grpc_test_openapi(load_app(client.application))

    def test_grpc_openapi_by_protobuf_file(self, client: FlaskClient) -> None:
        import os

        from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
        from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
        from pait.app.flask import load_app
        from pait.app.flask.grpc_route import GrpcGatewayRoute
        from pait.util.grpc_inspect.message_to_pydantic import grpc_timestamp_int_handler

        project_path: str = os.getcwd().split("pait/")[0]
        if project_path.endswith("pait"):
            project_path += "/"
        elif not project_path.endswith("pait/"):
            project_path = os.path.join(project_path, "pait/")
        grpc_path: str = project_path + "example/example_grpc/"

        prefix: str = "/api-test"

        GrpcGatewayRoute(
            client.application,
            user_pb2_grpc.UserStub,
            social_pb2_grpc.BookSocialStub,
            manager_pb2_grpc.BookManagerStub,
            prefix=prefix + "/",
            title="Grpc-test",
            grpc_timestamp_handler_tuple=(int, grpc_timestamp_int_handler),
            parse_msg_desc=grpc_path,
        )
        grpc_test_openapi(load_app(client.application), url_prefix=prefix)
