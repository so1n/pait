import asyncio
import difflib
import json
import random
import sys
from contextlib import contextmanager
from functools import partial
from typing import Any, Callable, Generator, Type
from unittest import mock

import pytest
from pydantic import BaseModel, Field
from pytest_mock import MockFixture
from redis import Redis  # type: ignore
from requests import Response  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from example.starlette_example import main_example
from pait.app import auto_load_app
from pait.app.any import get_app_attribute, set_app_attribute
from pait.app.base.simple_route import SimpleRoute
from pait.app.starlette import TestHelper as _TestHelper
from pait.app.starlette import add_multi_simple_route, add_simple_route, load_app, pait
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.model import response
from pait.model.context import ContextModel
from pait.openapi.doc_route import default_doc_fn_dict
from pait.openapi.openapi import InfoModel, OpenAPI, ServerModel
from tests.conftest import enable_plugin
from tests.test_app.base_api_test import BaseTest
from tests.test_app.base_doc_example_test import BaseTestDocExample
from tests.test_app.base_openapi_test import BaseTestOpenAPI

# Since the routing function has already been loaded,
# it will be automatically skipped when calling the load app later,
# and needs to be overwritten by overwrite already exists data=True
# flake8: noqa: F811
_TestHelper: Type[_TestHelper] = partial(  # type: ignore
    _TestHelper,
    load_app=partial(load_app, overwrite_already_exists_data=True),
    ignore_auto_found_http_method_set={"HEAD", "OPTIONS"},
)


@contextmanager
def client_ctx(app: Starlette = None, raise_server_exceptions: bool = True) -> Generator[TestClient, None, None]:
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
    # asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    if not app:
        app = main_example.create_app()
    with TestClient(app, raise_server_exceptions=raise_server_exceptions) as client:
        yield client


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with client_ctx() as client:
        yield client


@contextmanager
def base_test_ctx() -> Generator[BaseTest, None, None]:
    with client_ctx() as client:
        yield BaseTest(client, _TestHelper)


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    with base_test_ctx() as base_test:
        yield base_test


def response_test_helper(
    client: TestClient,
    route_handler: Callable,
    pait_response: Type[response.BaseResponseModel],
    plugin: Type[MockPlugin],
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
        app.add_route("/api/new-text-resp", main_example.text_response_route, methods=["GET", "POST"])
        with pytest.raises(RuntimeError) as e:
            _TestHelper(client, main_example.text_response_route).request()
        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_post(self, client: TestClient) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            main_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
            client.post(
                "/api/field/post",
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
                "/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
            # async route
            ("/api/plugin/async-check-json-plugin?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/plugin/async-check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url).json()
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_text_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, main_example.text_response_route, response.TextResponseModel, MockPlugin)
        response_test_helper(client, main_example.async_text_response_route, response.TextResponseModel, MockPlugin)

    def test_html_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, main_example.html_response_route, response.HtmlResponseModel, MockPlugin)
        response_test_helper(client, main_example.async_html_response_route, response.HtmlResponseModel, MockPlugin)

    def test_file_response(self, client: TestClient) -> None:
        from pait.app.starlette.plugin.mock_response import MockPlugin

        response_test_helper(client, main_example.file_response_route, response.FileResponseModel, MockPlugin)
        response_test_helper(client, main_example.async_file_response_route, response.FileResponseModel, MockPlugin)

    def test_doc_route(self, client: TestClient) -> None:
        main_example.add_api_doc_route(client.app)
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
            ][0]["example"]
            == "xxx"
        )
        assert (
            difflib.SequenceMatcher(
                None,
                str(client.get("/openapi.json?pin-code=6666").text),
                str(
                    OpenAPI(
                        client.app,  # type: ignore
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
        base_test.pait_base_field_route(main_example.pait_base_field_route)

    def test_param_at_most_one_of_route(self, base_test: BaseTest) -> None:
        base_test.param_at_most_one_of_route(main_example.param_at_most_one_of_route_by_extra_param)
        base_test.param_at_most_one_of_route(main_example.param_at_most_one_of_route)

    def test_param_required_route(self, base_test: BaseTest) -> None:
        base_test.param_required_route(main_example.param_required_route_by_extra_param)
        base_test.param_required_route(main_example.param_required_route)

    def test_check_response(self, base_test: BaseTest) -> None:
        base_test.check_response(main_example.check_response_route)

    def test_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(main_example.mock_route)

    def test_async_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(main_example.async_mock_route)

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(main_example.pait_model_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(main_example.depend_contextmanager_route, mocker)

    def test_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(main_example.depend_async_contextmanager_route, mocker)

    def test_pre_depend_async_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(main_example.pre_depend_async_contextmanager_route, mocker)

    def test_sync_to_thread(self, base_test: BaseTest, mocker: MockFixture) -> None:
        logger = mocker.patch("asyncio.log.logger.warning")
        base_test.base_sync_depend_route(main_example.sync_depend_route, {"body_dict": {"uid": 10086, "name": "so1n"}})
        base_test.base_sync_depend_route(main_example.sync_body_route, {"body_dict": {"uid": 10086, "name": "so1n"}})
        base_test.base_sync_depend_route(
            main_example.sync_with_ctx_depend_route, {"body_dict": {"uid": 10086, "name": "so1n"}}
        )
        assert logger.call_args is None

    def test_api_key_route(self, base_test: BaseTest) -> None:
        base_test.api_key_route(main_example.api_key_cookie_route, {"cookie_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_header_route, {"header_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_query_route, {"query_dict": {"token": "my-token"}})

    def test_oauth2_password_route(self, base_test: BaseTest) -> None:
        base_test.oauth2_password_route(
            login_route=main_example.oauth2_login,
            user_name_route=main_example.oauth2_user_name,
            user_info_route=main_example.oauth2_user_info,
        )

    def test_get_user_name_by_http_bearer(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_bearer(main_example.get_user_name_by_http_bearer)

    def test_get_user_name_by_http_digest(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_digest(main_example.get_user_name_by_http_digest)

    def test_get_user_name_by_http_basic_credentials(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_basic_credentials(main_example.get_user_name_by_http_basic_credentials)

    def test_get_cbv(self, base_test: BaseTest) -> None:
        base_test.get_cbv(main_example.CbvRoute.get)

    def test_post_cbv(self, base_test: BaseTest) -> None:
        base_test.post_cbv(main_example.CbvRoute.post)

    def test_cache_response(self, base_test: BaseTest) -> None:
        base_test.cache_response(main_example.cache_response, main_example.cache_response1, app="starlette")

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        main_example.CacheResponsePlugin.set_redis_to_app(base_test.client.app, Redis(decode_responses=True))
        base_test.cache_other_response_type(
            main_example.text_response_route,
            main_example.html_response_route,
            main_example.CacheResponsePlugin,
        )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        base_test.cache_response_param_name(
            main_example.post_route,
            main_example.CacheResponsePlugin,
            main_example.Redis(decode_responses=True),
        )

    def test_unified_response(self, base_test: BaseTest) -> None:
        base_test.unified_json_response(main_example.unified_json_response)
        base_test.unified_text_response(main_example.unified_text_response)
        base_test.unified_html_response(main_example.unified_html_response)

    def test_load_app_by_mount_route(self, client: TestClient) -> None:
        from starlette.responses import JSONResponse
        from starlette.routing import Mount, Route

        from pait.field import Query

        app: Starlette = client.app  # type: ignore

        @pait()
        def demo(a: int = Query.i()) -> JSONResponse:
            return JSONResponse({"a": a})

        key = "tests.test_app.test_starlette_TestStarlette.test_load_app_by_mount_route.<locals>.demo"

        assert key not in load_app(app)
        app.router.routes.append(Mount("/api/demo/mount/", routes=[Route("/demo", demo, methods=["GET"])]))
        reload_result = load_app(app)
        assert key in reload_result
        demo_core_model = load_app(app)[key]._core_model  # type: ignore[attr-defined]
        assert demo_core_model.path == "/api/demo/mount/demo"

    def test_load_app_by_other_route(self, client: TestClient, mocker: MockFixture) -> None:
        from starlette.responses import JSONResponse
        from starlette.routing import Host, Route, Router

        from pait.field import Query

        app: Starlette = client.app  # type: ignore

        @pait()
        def demo(a: int = Query.i()) -> JSONResponse:
            return JSONResponse({"a": a})

        demo_router = Router(routes=[Route("/", demo, methods=["GET"])])

        warn_logger = mocker.patch("pait.app.starlette._load_app.logging.warning")
        app.router.routes.append(Host("www.example.com", demo_router))
        assert "test_load_app_by_mount.<locals>.demo" not in load_app(app)

        warn_logger.assert_called_once_with(f"load_app func not support route:{Host}")

    def test_check_json_resp_plugin(self, pait_context: ContextModel) -> None:
        from starlette.responses import HTMLResponse, JSONResponse

        from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin

        assert CheckJsonRespPlugin.get_json(JSONResponse({"demo": 1}), pait_context) == {"demo": 1}

        with pytest.raises(TypeError):
            CheckJsonRespPlugin.get_json(object, pait_context)

        with pytest.raises(ValueError):
            CheckJsonRespPlugin.get_json(HTMLResponse(), pait_context)

        class MyCheckJsonRespPlugin(CheckJsonRespPlugin):
            json_media_type: str = "application/fake_json"

        assert MyCheckJsonRespPlugin.get_json(
            JSONResponse({"demo": 1}, media_type="application/fake_json"), pait_context
        ) == {"demo": 1}

    def test_gen_response(self) -> None:
        from starlette.responses import JSONResponse

        from pait.app.starlette.adapter.response import gen_response
        from pait.model import response

        result = gen_response(JSONResponse({"demo": 1}), response.BaseResponseModel)
        assert result.body == b'{"demo":1}'

        result = gen_response({"demo": 1}, response.JsonResponseModel)
        assert result.body == b'{"demo":1}'

        class HeaderModel(BaseModel):
            demo: str = Field(alias="x-demo", example="123")

        class MyHtmlResponseModel(response.HtmlResponseModel):
            media_type = "application/demo"
            header = HeaderModel
            status_code = (400,)

        result = gen_response("demo", MyHtmlResponseModel)
        assert result.body == b"demo"
        assert result.media_type == "application/demo"
        assert result.headers["x-demo"] == "123"
        assert result.status_code == 400

    def test_simple_route(self, client: TestClient) -> None:
        def simple_route_factory(num: int) -> Callable:
            @pait(response_model_list=[response.HtmlResponseModel])
            def simple_route() -> str:
                return f"I'm simple route {num}"

            simple_route.__name__ = simple_route.__name__ + str(num)
            return simple_route

        add_simple_route(
            client.app, SimpleRoute(methods=["GET"], url="/api/demo/simple-route-1", route=simple_route_factory(1))
        )
        add_multi_simple_route(
            client.app,
            SimpleRoute(methods=["GET"], url="/demo/simple-route-2", route=simple_route_factory(2)),
            SimpleRoute(methods=["GET"], url="/demo/simple-route-3", route=simple_route_factory(3)),
            prefix="/api",
            title="test",
        )
        assert client.get("/api/demo/simple-route-1").text == "I'm simple route 1"
        assert client.get("/api/demo/simple-route-2").text == "I'm simple route 2"
        assert client.get("/api/demo/simple-route-2").text == "I'm simple route 2"

    def test_any_type_route(self, base_test: BaseTest) -> None:
        base_test.any_type(main_example.any_type_route)

    def test_tag_route(self, base_test: BaseTest) -> None:
        base_test.tag(main_example.tag_route)

    def test_openapi_content(self, base_test: BaseTest) -> None:
        BaseTestOpenAPI(base_test.client.app).test_all()


class TestStarletteExtra:
    def test_request_extend(self) -> None:
        from pait.app.starlette.adapter.request import RequestExtend

        demo_req: Request

        async def app(scope: Any, receive: Any, send: Any) -> None:
            nonlocal demo_req
            demo_req = Request(scope, receive)
            resp = JSONResponse("")
            await resp(scope, receive, send)

        TestClient(app).get("http://127.0.0.1:8000/api/demo?a=123")
        request_extend = RequestExtend(demo_req)
        assert request_extend.scheme == "http"
        assert request_extend.path == "/api/demo"
        assert request_extend.hostname == "127.0.0.1:8000"


class TestDocExample:
    def test_hello_world_demo(self) -> None:
        from docs_source_code.introduction import starlette_demo

        with client_ctx(app=starlette_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(starlette_demo.demo_post)

    def test_pait_hello_world_demo(self) -> None:
        from docs_source_code.introduction import starlette_pait_hello_world_demo

        with client_ctx(app=starlette_pait_hello_world_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(starlette_pait_hello_world_demo.demo_post)

    def test_how_to_use_field_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_demo

        with client_ctx(app=starlette_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_demo(starlette_demo.demo_route)

    def test_how_to_use_field_with_default_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_default_demo

        with client_ctx(app=starlette_with_default_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_demo(
                starlette_with_default_demo.demo, starlette_with_default_demo.demo1
            )

    def test_how_to_use_field_with_default_factory_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_default_factory_demo

        with client_ctx(app=starlette_with_default_factory_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_factory_demo(
                starlette_with_default_factory_demo.demo, starlette_with_default_factory_demo.demo1
            )

    def test_how_to_use_field_with_alias_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_alias_demo

        with client_ctx(app=starlette_with_alias_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_alias_demo(starlette_with_alias_demo.demo)

    def test_how_to_use_field_with_number_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_num_check_demo

        with client_ctx(app=starlette_with_num_check_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_number_verify_demo(
                starlette_with_num_check_demo.demo
            )

    def test_how_to_use_field_with_sequence_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_item_check_demo

        with client_ctx(app=starlette_with_item_check_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_sequence_verify_demo(
                starlette_with_item_check_demo.demo
            )

    def test_how_to_use_field_with_str_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_string_check_demo

        with client_ctx(app=starlette_with_string_check_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_str_verify_demo(
                starlette_with_string_check_demo.demo
            )

    def test_how_to_use_field_with_raw_return_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_raw_return_demo

        with client_ctx(app=starlette_with_raw_return_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_raw_return_demo(
                starlette_with_raw_return_demo.demo
            )

    def test_how_to_use_field_with_custom_not_found_exc_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import starlette_with_not_found_exc_demo

        with client_ctx(app=starlette_with_not_found_exc_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_custom_not_found_exc_demo(
                starlette_with_not_found_exc_demo.demo
            )

    def test_how_to_use_type_with_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import starlette_with_model_demo

        with client_ctx(app=starlette_with_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pydantic_basemodel(
                starlette_with_model_demo.demo, starlette_with_model_demo.demo1
            )

    def test_how_to_use_type_with_pait_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import starlette_with_pait_model_demo

        with client_ctx(app=starlette_with_pait_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pait_basemodel(
                starlette_with_pait_model_demo.demo, starlette_with_pait_model_demo.demo1
            )

    def test_how_to_use_type_with_request_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import starlette_with_request_demo

        with client_ctx(app=starlette_with_request_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_request(
                starlette_with_request_demo.demo
            )

    def test_how_to_use_type_with_unix_datetime_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import starlette_with_unix_datetime_demo

        with client_ctx(app=starlette_with_unix_datetime_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_customer(
                starlette_with_unix_datetime_demo.demo
            )

    def test_depend_with_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import starlette_with_depend_demo

        with client_ctx(app=starlette_with_depend_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_depend(starlette_with_depend_demo.demo)

    def test_depend_with_nested_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import starlette_with_nested_depend_demo

        with client_ctx(app=starlette_with_nested_depend_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_nested_depend(starlette_with_nested_depend_demo.demo)

    def test_depend_with_context_manager_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import starlette_with_context_manager_depend_demo

        with client_ctx(app=starlette_with_context_manager_depend_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_context_manager_depend(
                starlette_with_context_manager_depend_demo.demo
            )

    def test_depend_with_class_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import starlette_with_class_depend_demo

        with client_ctx(app=starlette_with_class_depend_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_class_depend(starlette_with_class_depend_demo.demo)

    def test_depend_with_pre_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import starlette_with_pre_depend_demo

        with client_ctx(app=starlette_with_pre_depend_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_pre_depend(starlette_with_pre_depend_demo.demo)

    def test_exception_with_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import starlette_with_exception_demo

        with client_ctx(app=starlette_with_exception_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(starlette_with_exception_demo.demo)

    def test_exception_with_not_use_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import starlette_with_not_tip_exception_demo

        with client_ctx(app=starlette_with_not_tip_exception_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(starlette_with_not_tip_exception_demo.demo)

    def test_openapi_security_with_api_key(self) -> None:
        from docs_source_code.openapi.security import starlette_with_apikey_demo

        with client_ctx(app=starlette_with_apikey_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_api_key(
                starlette_with_apikey_demo.api_key_cookie_route,
                starlette_with_apikey_demo.api_key_header_route,
                starlette_with_apikey_demo.api_key_query_route,
            )

    def test_openapi_security_with_http(self) -> None:
        from docs_source_code.openapi.security import starlette_with_http_demo

        with client_ctx(app=starlette_with_http_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_http(
                starlette_with_http_demo.get_user_name_by_http_basic_credentials,
                starlette_with_http_demo.get_user_name_by_http_bearer,
                starlette_with_http_demo.get_user_name_by_http_digest,
            )

    def test_openapi_security_with_oauth2(self) -> None:
        from docs_source_code.openapi.security import starlette_with_oauth2_demo

        with client_ctx(app=starlette_with_oauth2_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_oauth2(
                starlette_with_oauth2_demo.oauth2_login,
                starlette_with_oauth2_demo.oauth2_user_info,
                starlette_with_oauth2_demo.oauth2_user_name,
            )

    def test_plugin_with_required_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            starlette_with_required_plugin_and_extra_param_demo,
            starlette_with_required_plugin_and_group_extra_param_demo,
            starlette_with_required_plugin_demo,
        )

        with client_ctx(app=starlette_with_required_plugin_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                starlette_with_required_plugin_demo.demo
            )
        with client_ctx(
            app=starlette_with_required_plugin_and_group_extra_param_demo.app, raise_server_exceptions=False
        ) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                starlette_with_required_plugin_and_group_extra_param_demo.demo
            )
        with client_ctx(
            app=starlette_with_required_plugin_and_extra_param_demo.app, raise_server_exceptions=False
        ) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                starlette_with_required_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_at_most_of_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            starlette_with_at_most_one_of_plugin_and_extra_param_demo,
            starlette_with_at_most_one_of_plugin_demo,
        )

        with client_ctx(app=starlette_with_at_most_one_of_plugin_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                starlette_with_at_most_one_of_plugin_demo.demo
            )
        with client_ctx(
            app=starlette_with_at_most_one_of_plugin_and_extra_param_demo.app, raise_server_exceptions=False
        ) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                starlette_with_at_most_one_of_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_check_json_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import starlette_with_check_json_plugin_demo

        with client_ctx(app=starlette_with_check_json_plugin_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_check_json_response_plugin(
                starlette_with_check_json_plugin_demo.demo
            )

    def test_plugin_with_auto_complete_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import starlette_with_auto_complete_json_plugin_demo

        with client_ctx(app=starlette_with_auto_complete_json_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_auto_complete_json_response_plugin(
                starlette_with_auto_complete_json_plugin_demo.demo
            )

    def test_plugin_with_mock_plugin(self) -> None:
        from docs_source_code.plugin.mock_plugin import starlette_with_mock_plugin_demo

        with client_ctx(app=starlette_with_mock_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_mock_plugin(starlette_with_mock_plugin_demo.demo)

    def test_plugin_with_cache_plugin(self) -> None:
        from docs_source_code.plugin.cache_plugin import starlette_with_cache_plugin_demo

        with client_ctx(app=starlette_with_cache_plugin_demo.app, raise_server_exceptions=False) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_cache_plugin(starlette_with_cache_plugin_demo.demo)
