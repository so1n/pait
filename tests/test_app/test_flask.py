import difflib
import json
import random
import sys
from contextlib import contextmanager
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from flask import Flask, Response
from flask.ctx import AppContext
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from werkzeug.test import _TestCookieJar

from example.common import response_model
from example.flask_example import grpc_route, main_example
from pait.app import auto_load_app, get_app_attribute, set_app_attribute
from pait.app.flask import TestHelper as _TestHelper
from pait.model import response
from pait.openapi.doc_route import default_doc_fn_dict
from pait.openapi.openapi import InfoModel, OpenAPI, ServerModel
from tests.conftest import enable_plugin, grpc_request_test, grpc_test_openapi
from tests.test_app.base_api_test import BaseTest
from tests.test_app.base_openapi_test import BaseTestOpenAPI


@contextmanager
def client_ctx() -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    app: Flask = main_example.create_app()
    client: FlaskClient = app.test_client()
    # Establish an application context before running the tests.
    ctx: AppContext = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    with client_ctx() as client:
        yield client


@contextmanager
def base_test_ctx() -> Generator[BaseTest, None, None]:
    with client_ctx() as client:
        yield BaseTest(client, _TestHelper)


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    with client_ctx() as client:
        yield BaseTest(client, _TestHelper)


def response_test_helper(
    client: FlaskClient, route_handler: Callable, pait_response: Type[response.BaseResponseModel]
) -> None:
    from pait.app.flask.plugin.mock_response import MockPlugin

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, MockPlugin.build()):
        resp: Response = test_helper.get()

        for key, value in pait_response.get_header_example_dict().items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.HtmlResponseModel) or issubclass(
            pait_response, response.TextResponseModel
        ):
            assert resp.get_data().decode() == pait_response.get_example_value()
        else:
            assert resp.get_data() == pait_response.get_example_value()


class TestFlask:
    def test_post(self, client: FlaskClient) -> None:
        flask_test_helper: _TestHelper = _TestHelper(
            client,
            main_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            flask_test_helper.json(),
            client.post(
                "/api/field/post",
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
                "/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url).get_json()
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_test_helper_not_support_mutil_method(self, client: FlaskClient) -> None:
        client.application.add_url_rule(
            "/api/plugin/text-resp", view_func=main_example.text_response_route, methods=["GET", "POST"]
        )
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, main_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self) -> None:
        with client_ctx() as client:
            main_example.add_api_doc_route(client.application)
            for doc_route_path in default_doc_fn_dict.keys():
                assert client.get(f"/{doc_route_path}").status_code == 404
                assert client.get(f"/api-doc/{doc_route_path}").status_code == 200

            for doc_route_path, fn in default_doc_fn_dict.items():
                assert client.get(f"/{doc_route_path}?pin-code=6666").get_data().decode() == fn(
                    "http://localhost/openapi.json?pin-code=6666", title="Pait Api Doc(private)"
                )

            assert (
                json.loads(client.get("/openapi.json?pin-code=6666&template-token=xxx").get_data().decode())["paths"][
                    "/api/user"
                ]["get"]["parameters"][0]["schema"]["example"]
                == "xxx"
            )
            assert (
                difflib.SequenceMatcher(
                    None,
                    str(client.get("/openapi.json?pin-code=6666").get_data().decode()),
                    str(
                        OpenAPI(
                            client.application,
                            openapi_info_model=InfoModel(title="Pait Doc"),
                            server_model_list=[ServerModel(url="http://localhost")],
                        ).content()
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

    def test_app_attribute(self) -> None:
        with client_ctx() as client:
            key: str = "app_test_app_attribute"
            value: int = random.randint(1, 100)
            set_app_attribute(client.application, key, value)

            def demo_route() -> dict:
                assert get_app_attribute(client.application, key) == value
                return {}

            url: str = "/api/test-invoke-demo"
            client.application.add_url_rule(url, view_func=demo_route)
            assert client.get(url).json == {}

    def test_text_response(self, client: FlaskClient) -> None:
        response_test_helper(client, main_example.text_response_route, response.TextResponseModel)

    def test_html_response(self, client: FlaskClient) -> None:
        response_test_helper(client, main_example.html_response_route, response.HtmlResponseModel)

    def test_file_response(self, client: FlaskClient) -> None:
        response_test_helper(client, main_example.file_response_route, response.FileResponseModel)

    def test_raise_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_tip_route, mocker=mocker)

    def test_raise_not_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_not_tip_route, mocker=mocker, is_raise=False)

    def test_auto_complete_json_route(self, base_test: BaseTest) -> None:
        base_test.auto_complete_json_route(main_example.auto_complete_json_route)

    def test_depend_route(self, base_test: BaseTest) -> None:
        base_test.depend_route(main_example.depend_route)

    def test_same_alias_name(self, base_test: BaseTest) -> None:
        base_test.same_alias_name(main_example.same_alias_route)

    def test_field_default_factory_route(self, base_test: BaseTest) -> None:
        base_test.field_default_factory_route(main_example.field_default_factory_route)

    def test_pait_base_field_route(self, base_test: BaseTest) -> None:
        base_test.pait_base_field_route(main_example.pait_base_field_route, ignore_path=False)

    def test_param_at_most_one_of_route(self, base_test: BaseTest) -> None:
        base_test.param_at_most_one_of_route(main_example.param_at_most_onf_of_route_by_extra_param)
        base_test.param_at_most_one_of_route(main_example.param_at_most_onf_of_route)

    def test_param_required_route(self, base_test: BaseTest) -> None:
        base_test.param_required_route(main_example.param_required_route_by_extra_param)
        base_test.param_required_route(main_example.param_required_route)

    def test_check_response(self, base_test: BaseTest) -> None:
        base_test.check_response(main_example.check_response_route)

    def test_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(main_example.mock_route, response_model.UserSuccessRespModel2)

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(main_example.pait_model_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(main_example.depend_contextmanager_route, mocker)

    def test_pre_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(main_example.pre_depend_contextmanager_route, mocker)

    def test_api_key_route(self, base_test: BaseTest) -> None:
        # clear cookie
        base_test.client.cookie_jar = _TestCookieJar()
        base_test.api_key_route(main_example.api_key_cookie_route, {"cookie_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_header_route, {"header_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_query_route, {"query_dict": {"token": "my-token"}})

    def test_get_user_name_by_http_bearer(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_bearer(main_example.get_user_name_by_http_bearer)

    def test_get_user_name_by_http_digest(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_digest(main_example.get_user_name_by_http_digest)

    def test_get_user_name_by_http_basic_credentials(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_basic_credentials(main_example.get_user_name_by_http_basic_credentials)

    def test_oauth2_password_route(self, base_test: BaseTest) -> None:
        base_test.oauth2_password_route(
            login_route=main_example.oauth2_login,
            user_name_route=main_example.oauth2_user_name,
            user_info_route=main_example.oauth2_user_info,
        )

    def test_get_cbv(self, base_test: BaseTest) -> None:
        base_test.get_cbv(main_example.CbvRoute.get)

    def test_post_cbv(self, base_test: BaseTest) -> None:
        base_test.post_cbv(main_example.CbvRoute.post)

    def test_cache_response(self, base_test: BaseTest) -> None:
        base_test.cache_response(main_example.cache_response, main_example.cache_response1)

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        main_example.CacheResponsePlugin.set_redis_to_app(
            base_test.client.application, main_example.Redis(decode_responses=True)
        )
        base_test.cache_other_response_type(
            main_example.text_response_route, main_example.html_response_route, main_example.CacheResponsePlugin
        )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        base_test.cache_response_param_name(
            main_example.post_route, main_example.CacheResponsePlugin, main_example.Redis(decode_responses=True)
        )

    def test_openapi_content(self, base_test: BaseTest) -> None:
        BaseTestOpenAPI(base_test.client.application).test_all()


class TestFlaskGrpc:
    def test_create_user(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.user.user_pb2 import CreateUserRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in ("/api/user/create", "/api/static/user/create"):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(
                        url,
                        json={"uid": "10086", "user_name": "so1n", "pw": "123456", "sex": 0},
                    ).data
                    assert body == b'{"code":0,"data":{},"msg":""}\n'
                    message: CreateUserRequest = queue.get(timeout=1)
                    assert message.uid == "10086"
                    assert message.user_name == "so1n"
                    assert message.password == "123456"
                    assert message.sex == 0

    def test_get_book(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.book.manager_pb2 import GetBookRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in (
                "/api/book/get",
                "/api/static/book/get",
            ):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(url + "?isbn=xxxa", headers={"token": "token"}).data
                    assert body == (
                        b'{"code":0,'
                        b'"data":{"book_author":"","book_desc":"","book_name":"","book_url":"","isbn":""},"msg":""}\n'
                    )
                    queue.get(timeout=1)
                    message: GetBookRequest = queue.get(timeout=1)
                    assert message.isbn == "xxxa"

    def test_get_book_list(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.book.manager_pb2 import GetBookListRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in (
                "/api/book/get-list",
                "/api/static/book/get-list",
            ):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(
                        url, json={"limit": 0, "next_create_time": "2023-04-10 18:44:36"}, headers={"token": "token"}
                    ).data
                    assert body == (b'{"code":0,"data":[],"msg":""}\n')
                    queue.get(timeout=1)
                    message: GetBookListRequest = queue.get(timeout=1)
                    assert message.limit == 0

    def test_get_book_like(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.book.social_pb2 import (
            GetBookLikesRequest,
            NestedGetBookLikesRequest,
        )

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in (
                "/api/book/get-book-like",
                "/api/book/get-book-like-other",
                "/api/static/book/get-book-like",
                "/api/static/book/get-book-like-other",
            ):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(url, json={"isbn": ["xxxa", "xxxb"]}, headers={"token": "token"}).data
                    assert body == b'{"code":0,"data":{"result":[]},"msg":""}\n'
                    queue.get(timeout=1)
                    if not url.endswith("other"):
                        message1: GetBookLikesRequest = queue.get(timeout=1)
                        assert message1.isbn == ["xxxa", "xxxb"]
                    else:
                        message2: NestedGetBookLikesRequest = queue.get(timeout=1)
                        assert message2.nested.isbn == ["xxxa", "xxxb"]

    def test_login(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.user.user_pb2 import LoginUserRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in ("/api/user/login", "/api/static/user/login"):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(url, json={"uid": "10086", "password": "pw"}).data
                    assert body == b'{"code":0,"data":{"token":"","uid":"","user_name":""},"msg":""}\n'
                    message: LoginUserRequest = queue.get(timeout=1)
                    assert message.uid == "10086"
                    assert message.password == "pw"

    def test_logout(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.user.user_pb2 import LogoutUserRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in ("/api/user/logout", "/api/static/user/logout"):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(url, json={"uid": "10086"}, headers={"token": "token"}).data
                    assert body == b'{"code":0,"data":{},"msg":""}\n'
                    message: LogoutUserRequest = queue.get(timeout=1)
                    assert message.uid == "10086"
                    assert message.token == "token"

    def test_delete_fail_token(self) -> None:
        from example.grpc_common.python_example_proto_code.example_proto.user.user_pb2 import GetUidByTokenRequest

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in ("/api/user/delete", "/api/static/user/delete"):
                with grpc_request_test(client.application) as queue:
                    body: bytes = client.post(
                        url,
                        json={"uid": "10086"},
                        headers={"token": "fail_token"},
                    ).data
                    assert body == b'{"code":-1,"msg":"Not found user by token:fail_token"}\n'
                    message: GetUidByTokenRequest = queue.get(timeout=1)
                    assert message.token == "fail_token"

    def test_nested_demo(self) -> None:
        pass

        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)
            main_example.add_api_doc_route(client.application)

            for url in ("/api/other/nested-demo", "/api/static/other/nested-demo"):
                with grpc_request_test(client.application):
                    body: bytes = client.post(url, headers={"token": "token"}).data
                    assert body == b'{"code":0,"data":{"a":[{"map_demo":{"c":[{"a":1,"b":"foo"}]}}]},"msg":""}\n'

    def test_grpc_openapi(self) -> None:
        with client_ctx() as client:
            grpc_route.add_grpc_gateway_route(client.application)

            grpc_test_openapi(client.application)
            grpc_test_openapi(client.application, url_prefix="/api/static", option_str="_by_option")

    def test_grpc_openapi_by_protobuf_file(self) -> None:
        from pait.grpc import GrpcGatewayRoute

        with base_test_ctx() as base_test:
            base_test.grpc_openapi_by_protobuf_file(base_test.client.application, GrpcGatewayRoute)

    def test_grpc_openapi_by_option(self) -> None:
        from pait.grpc import GrpcGatewayRoute

        with base_test_ctx() as base_test:
            base_test.grpc_openapi_by_option(base_test.client.application, GrpcGatewayRoute)
