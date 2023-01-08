import difflib
import json
import random
import sys
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from pytest_mock import MockFixture
from redis import Redis  # type: ignore
from sanic import Sanic
from sanic_testing import TestManager as SanicTestManager  # type: ignore
from sanic_testing.testing import SanicTestClient
from sanic_testing.testing import TestingResponse as Response  # type: ignore

from example.param_verify import sanic_example
from pait.api_doc.openapi import InfoModel, OpenAPI, ServerModel
from pait.app import auto_load_app, get_app_attribute, set_app_attribute
from pait.app.base.doc_route import default_doc_fn_dict
from pait.app.sanic import TestHelper as _TestHelper
from pait.app.sanic import load_app
from pait.model import response
from tests.conftest import enable_plugin, fixture_loop, grpc_test_create_user_request, grpc_test_openapi
from tests.test_app.base_test import BaseTest


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    app: Sanic = sanic_example.create_app()
    SanicTestManager(app)
    yield app.test_client


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    app: Sanic = sanic_example.create_app()
    SanicTestManager(app)
    yield BaseTest(app.test_client, _TestHelper)


def response_test_helper(
    client: SanicTestClient, route_handler: Callable, pait_response: Type[response.BaseResponseModel]
) -> None:
    from pait.app.sanic.plugin.mock_response import MockPlugin

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, MockPlugin.build()):
        resp: Response = test_helper.get()
        for key, value in pait_response.get_header_example_dict().items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.HtmlResponseModel) or issubclass(
            pait_response, response.TextResponseModel
        ):
            assert resp.text == pait_response.get_example_value()
        else:
            assert resp.content == pait_response.get_example_value()


class TestSanic:
    def test_post(self, client: SanicTestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            sanic_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
            client.post(
                "/api/post",
                headers={"user-agent": "customer_agent"},
                json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )[1].json,
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
            }

    def test_check_json_route(self, client: SanicTestClient) -> None:
        for url, api_code in [
            (
                "/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url)[1].json
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_test_helper_not_support_mutil_method(self, client: SanicTestClient) -> None:
        client.app.add_route(sanic_example.text_response_route, "/api/new-text-resp", methods={"GET", "POST"})
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, sanic_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self, client: SanicTestClient) -> None:
        sanic_example.add_api_doc_route(client.app)
        for doc_route_path in default_doc_fn_dict.keys():
            assert client.get(f"/{doc_route_path}")[1].status_code == 404
            assert client.get(f"/api-doc/{doc_route_path}")[1].status_code == 200

        for doc_route_path, fn in default_doc_fn_dict.items():
            assert client.get(f"/{doc_route_path}?pin_code=6666")[1].text == fn(
                f"http://{client.host}:{client.port}/openapi.json?pin_code=6666", title="Pait Api Doc(private)"
            )

        assert (
            json.loads(client.get("/openapi.json?pin_code=6666&template-token=xxx")[1].text)["paths"]["/api/user"][
                "get"
            ]["parameters"][0]["schema"]["example"]
            == "xxx"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(client.get("/openapi.json?pin_code=6666")[1].text),
                str(
                    OpenAPI(
                        load_app(client.app),
                        openapi_info_model=InfoModel(title="Pait Doc"),
                        server_model_list=[ServerModel(url="http://localhost")],
                    ).content()
                ),
            ).quick_ratio()
            > 0.95
        )

    def test_text_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.text_response_route, response.TextResponseModel)

    def test_html_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.html_response_route, response.HtmlResponseModel)

    def test_file_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, sanic_example.file_response_route, response.FileResponseModel)

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import sanic

        with mock.patch.dict("sys.modules", sys.modules):
            assert sanic == auto_load_app.auto_load_app_class()

    def test_app_attribute(self, client: SanicTestClient) -> None:
        key: str = "test_app_attribute"
        value: int = random.randint(1, 100)
        set_app_attribute(client.app, key, value)
        assert get_app_attribute(client.app, key) == value

    def test_raise_tip_route(self, base_test: BaseTest) -> None:
        base_test.raise_tip_route(sanic_example.raise_tip_route)

    def test_auto_complete_json_route(self, base_test: BaseTest) -> None:
        base_test.auto_complete_json_route(sanic_example.auto_complete_json_route)

    def test_depend_route(self, base_test: BaseTest) -> None:
        base_test.depend_route(sanic_example.depend_route)

    def test_same_alias_name(self, base_test: BaseTest) -> None:
        base_test.same_alias_name(sanic_example.same_alias_route)

    def test_field_default_factory_route(self, base_test: BaseTest) -> None:
        base_test.field_default_factory_route(sanic_example.field_default_factory_route)

    def test_pait_base_field_route(self, base_test: BaseTest) -> None:
        base_test.pait_base_field_route(sanic_example.pait_base_field_route)

    def test_check_param(self, base_test: BaseTest) -> None:
        base_test.check_param(sanic_example.check_param_route)

    def test_check_response(self, base_test: BaseTest) -> None:
        base_test.check_response(sanic_example.check_response_route)

    def test_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(sanic_example.mock_route, sanic_example.UserSuccessRespModel2)

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(sanic_example.pait_model_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(sanic_example.depend_contextmanager_route, mocker)

    def test_pre_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(sanic_example.pre_depend_contextmanager_route, mocker)

    def test_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(sanic_example.depend_async_contextmanager_route, mocker)

    def test_pre_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(sanic_example.pre_depend_async_contextmanager_route, mocker)

    def test_get_cbv(self, base_test: BaseTest) -> None:
        base_test.get_cbv(sanic_example.CbvRoute.get)

    def test_post_cbv(self, base_test: BaseTest) -> None:
        base_test.post_cbv(sanic_example.CbvRoute.post)

    def test_cache_response(self, base_test: BaseTest) -> None:
        with fixture_loop(mock_close_loop=True):
            base_test.cache_response(sanic_example.cache_response, sanic_example.cache_response1)

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        with fixture_loop(mock_close_loop=True):
            sanic_example.CacheResponsePlugin.set_redis_to_app(
                base_test.client.app, sanic_example.Redis(decode_responses=True)
            )
            base_test.cache_other_response_type(
                sanic_example.text_response_route, sanic_example.html_response_route, sanic_example.CacheResponsePlugin
            )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        with fixture_loop(mock_close_loop=True):
            base_test.cache_response_param_name(
                sanic_example.post_route, sanic_example.CacheResponsePlugin, sanic_example.Redis(decode_responses=True)
            )


class TestSanicGrpc:
    def test_create_user(self, client: SanicTestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import CreateUserRequest

        sanic_example.add_grpc_gateway_route(client.app)
        sanic_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            request, response = client.post(
                "/api/user/create",
                json={"uid": "10086", "user_name": "so1n", "pw": "123456", "sex": 0},
                headers={"token": "token"},
            )
            assert response.body == b'{"code":0,"msg":"","data":{}}'
            message: CreateUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.user_name == "so1n"
            assert message.password == "123456"
            assert message.sex == 0

    def test_login(self, client: SanicTestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import LoginUserRequest

        sanic_example.add_grpc_gateway_route(client.app)
        sanic_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            request, response = client.post("/api/user/login", json={"uid": "10086", "password": "pw"})
            assert response.body == b'{"code":0,"msg":"","data":{}}'
            message: LoginUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.password == "pw"

    def test_logout(self, client: SanicTestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import LogoutUserRequest

        sanic_example.add_grpc_gateway_route(client.app)
        sanic_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            request, response = client.post("/api/user/logout", json={"uid": "10086"}, headers={"token": "token"})
            assert response.body == b'{"code":0,"msg":"","data":{}}'
            message: LogoutUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.token == "token"

    def test_delete_fail_token(self, client: SanicTestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import GetUidByTokenRequest

        sanic_example.add_grpc_gateway_route(client.app)
        sanic_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            request, response = client.post(
                "/api/user/delete",
                json={"uid": "10086"},
                headers={"token": "fail_token"},
            )
            assert response.body == b'{"code":-1,"msg":"Not found user by token:fail_token"}'
            message: GetUidByTokenRequest = queue.get(timeout=1)
            assert message.token == "fail_token"

    def test_grpc_openapi(self, client: SanicTestClient) -> None:
        sanic_example.add_grpc_gateway_route(client.app)

        from pait.app.sanic import load_app

        grpc_test_openapi(load_app(client.app))

    def test_grpc_openapi_by_protobuf_file(self, base_test: BaseTest) -> None:
        from pait.app.sanic import load_app
        from pait.app.sanic.grpc_route import GrpcGatewayRoute

        base_test.grpc_openapi_by_protobuf_file(base_test.client.app, GrpcGatewayRoute, load_app)
