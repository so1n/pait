import asyncio
import difflib
import json
import random
import sys
from typing import Callable, Generator, Type, Union
from unittest import mock

import pytest
from pytest_mock import MockFixture
from requests import Response  # type: ignore
from starlette.applications import Starlette
from starlette.testclient import TestClient

from example.param_verify import starlette_example
from pait.app import auto_load_app, get_app_attribute, set_app_attribute
from pait.app.base.doc_route import default_doc_fn_dict
from pait.app.starlette import TestHelper as _TestHelper
from pait.app.starlette import load_app
from pait.model import response
from pait.openapi.openapi import InfoModel, OpenAPI, ServerModel
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin
from tests.conftest import enable_plugin, grpc_test_create_user_request, grpc_test_openapi
from tests.test_app.base_test import BaseTest


@pytest.fixture
def client(mocker: MockFixture) -> Generator[TestClient, None, None]:
    # starlette run after sanic
    # fix starlette.testclient get_event_loop status is close
    # def get_event_loop() -> asyncio.AbstractEventLoop:
    #     try:
    #         loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    #         if loop.is_closed():
    #             loop = asyncio.new_event_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #     return loop
    #
    # mocker.patch("asyncio.get_event_loop").return_value = get_event_loop()
    asyncio.set_event_loop(asyncio.new_event_loop())
    yield TestClient(starlette_example.create_app())


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    asyncio.set_event_loop(asyncio.new_event_loop())
    yield BaseTest(TestClient(starlette_example.create_app()), _TestHelper)


def response_test_helper(
    client: TestClient,
    route_handler: Callable,
    pait_response: Type[response.BaseResponseModel],
    plugin: Type[Union[BaseMockPlugin, BaseAsyncMockPlugin]],
) -> None:

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, plugin.build()):
        resp: Response = test_helper.get()
        for key, value in pait_response.get_header_example_dict().items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.HtmlResponseModel) or issubclass(
            pait_response, response.TextResponseModel
        ):
            assert resp.text == pait_response.get_example_value()
        else:
            assert resp.content == pait_response.get_example_value()


class TestStarlette:
    def test_test_helper_not_support_mutil_method(self, client: TestClient) -> None:
        app: Starlette = client.app  # type: ignore
        app.add_route("/api/new-text-resp", starlette_example.text_response_route, methods=["GET", "POST"])
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, starlette_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_post(self, client: TestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            starlette_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
            client.post(
                "/api/post",
                headers={"user-agent": "customer_agent"},
                json={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            ).json(),
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
            }

    def test_check_json_route(self, client: TestClient) -> None:
        for url, api_code in [
            # sync route
            (
                "/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            # async route
            (
                "/api/async-check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/async-check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            ("/api/async-check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/async-check-json-plugin-1?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url).json()
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_text_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, starlette_example.text_response_route, response.TextResponseModel, MockPlugin)
        response_test_helper(
            client, starlette_example.async_text_response_route, response.TextResponseModel, MockPlugin
        )

    def test_html_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, starlette_example.html_response_route, response.HtmlResponseModel, MockPlugin)
        response_test_helper(
            client, starlette_example.async_html_response_route, response.HtmlResponseModel, MockPlugin
        )

    def test_file_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, starlette_example.file_response_route, response.FileResponseModel, MockPlugin)
        response_test_helper(
            client, starlette_example.async_file_response_route, response.FileResponseModel, MockPlugin
        )

    def test_doc_route(self, client: TestClient) -> None:
        starlette_example.add_api_doc_route(client.app)
        for doc_route_path in default_doc_fn_dict.keys():
            assert client.get(f"/{doc_route_path}").status_code == 404
            assert client.get(f"/api-doc/{doc_route_path}").status_code == 200

        for doc_route_path, fn in default_doc_fn_dict.items():
            assert client.get(f"/{doc_route_path}?pin-code=6666").text == fn(
                f"{client.base_url}/openapi.json?pin-code=6666", title="Pait Api Doc(private)"
            )

        assert (
            json.loads(client.get("/openapi.json?pin-code=6666&template-token=xxx").text)["paths"]["/api/user"]["get"][
                "parameters"
            ][0]["schema"]["example"]
            == "xxx"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(client.get("/openapi.json?pin-code=6666").text),
                str(
                    OpenAPI(
                        load_app(client.app),  # type: ignore
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
        import starlette

        with mock.patch.dict("sys.modules", sys.modules):
            assert starlette == auto_load_app.auto_load_app_class()

    def test_app_attribute(self, client: TestClient) -> None:
        key: str = "test_app_attribute"
        value: int = random.randint(1, 100)
        set_app_attribute(client.app, key, value)
        assert get_app_attribute(client.app, key) == value

    def test_raise_tip_route(self, base_test: BaseTest) -> None:
        base_test.raise_tip_route(starlette_example.raise_tip_route)

    def test_auto_complete_json_route(self, base_test: BaseTest) -> None:
        base_test.auto_complete_json_route(starlette_example.auto_complete_json_route)

    def test_depend_route(self, base_test: BaseTest) -> None:
        base_test.depend_route(starlette_example.depend_route)

    def test_same_alias_name(self, base_test: BaseTest) -> None:
        base_test.same_alias_name(starlette_example.same_alias_route)

    def test_field_default_factory_route(self, base_test: BaseTest) -> None:
        base_test.field_default_factory_route(starlette_example.field_default_factory_route)

    def test_pait_base_field_route(self, base_test: BaseTest) -> None:
        base_test.pait_base_field_route(starlette_example.pait_base_field_route)

    def test_check_param(self, base_test: BaseTest) -> None:
        base_test.check_param(starlette_example.check_param_route)

    def test_check_response(self, base_test: BaseTest) -> None:
        base_test.check_response(starlette_example.check_response_route)

    def test_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(starlette_example.mock_route, starlette_example.UserSuccessRespModel2)

    def test_async_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(starlette_example.async_mock_route, starlette_example.UserSuccessRespModel2)

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(starlette_example.pait_model_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(starlette_example.depend_contextmanager_route, mocker)

    def test_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(starlette_example.depend_async_contextmanager_route, mocker)

    def test_pre_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(starlette_example.pre_depend_async_contextmanager_route, mocker)

    def test_get_cbv(self, base_test: BaseTest) -> None:
        base_test.get_cbv(starlette_example.CbvRoute.get)

    def test_post_cbv(self, base_test: BaseTest) -> None:
        base_test.post_cbv(starlette_example.CbvRoute.post)

    def test_cache_response(self, base_test: BaseTest) -> None:
        base_test.cache_response(starlette_example.cache_response, starlette_example.cache_response1, app="starlette")

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        starlette_example.CacheResponsePlugin.set_redis_to_app(
            base_test.client.app, starlette_example.Redis(decode_responses=True)
        )
        base_test.cache_other_response_type(
            starlette_example.text_response_route,
            starlette_example.html_response_route,
            starlette_example.CacheResponsePlugin,
        )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        base_test.cache_response_param_name(
            starlette_example.post_route,
            starlette_example.CacheResponsePlugin,
            starlette_example.Redis(decode_responses=True),
        )


class TestStarletteGrpc:
    def test_create_user(self, client: TestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import CreateUserRequest

        starlette_example.add_grpc_gateway_route(client.app)
        starlette_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            body: bytes = client.post(
                "/api/user/create",
                json={"uid": "10086", "user_name": "so1n", "pw": "123456", "sex": 0},
                headers={"token": "token"},
            ).content
            assert body == b'{"code":0,"msg":"","data":{}}'
            message: CreateUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.user_name == "so1n"
            assert message.password == "123456"
            assert message.sex == 0

    def test_login(self, client: TestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import LoginUserRequest

        starlette_example.add_grpc_gateway_route(client.app)
        starlette_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            body: bytes = client.post("/api/user/login", json={"uid": "10086", "password": "pw"}).content
            assert body == b'{"code":0,"msg":"","data":{}}'
            message: LoginUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.password == "pw"

    def test_logout(self, client: TestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import LogoutUserRequest

        starlette_example.add_grpc_gateway_route(client.app)
        starlette_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            body: bytes = client.post("/api/user/logout", json={"uid": "10086"}, headers={"token": "token"}).content
            assert body == b'{"code":0,"msg":"","data":{}}'
            message: LogoutUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.token == "token"

    def test_delete_fail_token(self, client: TestClient) -> None:
        from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import GetUidByTokenRequest

        starlette_example.add_grpc_gateway_route(client.app)
        starlette_example.add_api_doc_route(client.app)

        with grpc_test_create_user_request(client.app) as queue:
            body: bytes = client.post(
                "/api/user/delete",
                json={"uid": "10086"},
                headers={"token": "fail_token"},
            ).content
            assert body == b'{"code":-1,"msg":"Not found user by token:fail_token"}'
            message: GetUidByTokenRequest = queue.get(timeout=1)
            assert message.token == "fail_token"

    def test_grpc_openapi(self, client: TestClient) -> None:
        starlette_example.add_grpc_gateway_route(client.app)

        from pait.app.starlette import load_app

        with client:
            grpc_test_openapi(load_app(client.app))

    def test_grpc_openapi_by_protobuf_file(self, base_test: BaseTest) -> None:
        from pait.app.starlette import load_app
        from pait.app.starlette.grpc_route import GrpcGatewayRoute

        base_test.grpc_openapi_by_protobuf_file(base_test.client.app, GrpcGatewayRoute, load_app)
