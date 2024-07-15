import difflib
import json
import logging
import random
import sys
from contextlib import contextmanager
from functools import partial
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from pydantic import BaseModel, Field
from pytest_mock import MockFixture
from redis import Redis  # type: ignore
from sanic import Sanic
from sanic.request import Request
from sanic_testing import TestManager as SanicTestManager  # type: ignore
from sanic_testing.testing import SanicTestClient
from sanic_testing.testing import TestingResponse as Response  # type: ignore

from example.sanic_example import main_example
from pait.app import auto_load_app
from pait.app.any import get_app_attribute, set_app_attribute
from pait.app.base.simple_route import SimpleRoute
from pait.app.sanic import TestHelper as _TestHelper
from pait.app.sanic import add_multi_simple_route, add_simple_route, load_app, pait
from pait.model import response
from pait.model.context import ContextModel
from pait.openapi.doc_route import default_doc_fn_dict
from pait.openapi.openapi import InfoModel, OpenAPI, ServerModel
from tests.conftest import enable_plugin, fixture_loop
from tests.test_app.base_api_test import BaseTest
from tests.test_app.base_doc_example_test import BaseTestDocExample
from tests.test_app.base_openapi_test import BaseTestOpenAPI

# Since the routing function has already been loaded,
# it will be automatically skipped when calling the load app later,
# and needs to be overwritten by overwrite already exists data=True
# flake8: noqa: F811
_TestHelper: Type[_TestHelper] = partial(  # type: ignore
    _TestHelper, load_app=partial(load_app, overwrite_already_exists_data=True)
)


@contextmanager
def client_ctx(app: Sanic = None) -> Generator[SanicTestClient, None, None]:
    logging.disable()  # don't know where to configure the log, the test environment will be canceled log
    if not app:
        app = main_example.create_app(configure_logging=False)
    app.config.ACCESS_LOG = False
    yield app.test_client


@pytest.fixture
def client() -> Generator[SanicTestClient, None, None]:
    with client_ctx() as client:
        yield client


@contextmanager
def base_test_ctx() -> Generator[BaseTest, None, None]:
    logging.disable()  # don't know where to configure the log, the test environment will be canceled log
    app: Sanic = main_example.create_app(configure_logging=False)
    app.config.ACCESS_LOG = False
    yield BaseTest(app.test_client, _TestHelper)


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    with base_test_ctx() as base_test:
        yield base_test


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
                "/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url)[1].json
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_test_helper_not_support_mutil_method(self) -> None:
        with client_ctx() as client:
            client.app.add_route(main_example.text_response_route, "/api/new-text-resp", methods={"GET", "POST"})
            with pytest.raises(RuntimeError) as e:
                _TestHelper(client, main_example.text_response_route).request()
            exec_msg: str = e.value.args[0]
            assert exec_msg == "Pait Can not auto select method, please choice method in ['GET', 'POST']"

    def test_doc_route(self) -> None:
        with client_ctx() as client:
            main_example.add_api_doc_route(client.app)
            for doc_route_path in default_doc_fn_dict.keys():
                assert client.get(f"/{doc_route_path}")[1].status_code == 404
                assert client.get(f"/api-doc/{doc_route_path}")[1].status_code == 200

            for doc_route_path, fn in default_doc_fn_dict.items():
                assert client.get(f"/{doc_route_path}?pin-code=6666")[1].text == fn(
                    f"http://{client.host}:{client.port}/openapi.json?pin-code=6666", title="Pait Api Doc(private)"
                )

            assert (
                json.loads(client.get("/openapi.json?pin-code=6666&template-token=xxx")[1].text)["paths"]["/api/user"][
                    "get"
                ]["parameters"][0]["example"]
                == "xxx"
            )
            assert (
                difflib.SequenceMatcher(
                    None,
                    str(client.get("/openapi.json?pin-code=6666")[1].text),
                    str(
                        OpenAPI(
                            client.app,
                            openapi_info_model=InfoModel(title="Pait Doc"),
                            server_model_list=[ServerModel(url="http://localhost")],
                        ).content()
                    ),
                ).quick_ratio()
                > 0.95
            )

    def test_text_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, main_example.text_response_route, response.TextResponseModel)

    def test_html_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, main_example.html_response_route, response.HtmlResponseModel)

    def test_file_response(self, client: SanicTestClient) -> None:
        response_test_helper(client, main_example.file_response_route, response.FileResponseModel)

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

    def test_raise_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_tip_route, mocker=mocker)

    def test_raise_not_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_not_tip_route, mocker=mocker, is_raise=False)

    def test_new_raise_not_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.new_raise_not_tip_route, mocker=mocker, is_raise=False)

    def test_auto_complete_json_route(self, base_test: BaseTest) -> None:
        base_test.auto_complete_json_route(main_example.auto_complete_json_route)

    def test_depend_route(self, base_test: BaseTest) -> None:
        base_test.depend_route(main_example.depend_route)

    def test_pre_depend_route(self, base_test: BaseTest) -> None:
        base_test.pre_depend_route(main_example.pre_depend_route)

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

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(main_example.pait_model_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(main_example.depend_contextmanager_route, mocker)

    def test_pre_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(main_example.pre_depend_contextmanager_route, mocker)

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
        with fixture_loop(mock_close_loop=True):
            base_test.cache_response(main_example.cache_response, main_example.cache_response1, app="sanic")

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        with fixture_loop(mock_close_loop=True):
            main_example.CacheResponsePlugin.set_redis_to_app(
                base_test.client.app, main_example.Redis(decode_responses=True)
            )
            base_test.cache_other_response_type(
                main_example.text_response_route, main_example.html_response_route, main_example.CacheResponsePlugin
            )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        with fixture_loop(mock_close_loop=True):
            base_test.cache_response_param_name(
                main_example.post_route, main_example.CacheResponsePlugin, main_example.Redis(decode_responses=True)
            )

    def test_unified_response(self, base_test: BaseTest) -> None:
        base_test.unified_json_response(main_example.unified_json_response)
        base_test.unified_text_response(main_example.unified_text_response)
        base_test.unified_html_response(main_example.unified_html_response)

    def test_check_json_resp_plugin(self, pait_context: ContextModel) -> None:
        from sanic.response import HTTPResponse
        from sanic.response import json as json_resp

        from pait.app.sanic.plugin.check_json_resp import CheckJsonRespPlugin

        assert CheckJsonRespPlugin.get_json(json_resp({"demo": 1}), pait_context) == {"demo": 1}
        demo_resp = json_resp({"demo": 1})
        demo_resp.body = json.dumps({"demo": 1})
        assert CheckJsonRespPlugin.get_json(demo_resp, pait_context) == {"demo": 1}

        with pytest.raises(TypeError):
            CheckJsonRespPlugin.get_json(object, pait_context)

        with pytest.raises(ValueError):
            CheckJsonRespPlugin.get_json(HTTPResponse(), pait_context)

        class MyCheckJsonRespPlugin(CheckJsonRespPlugin):
            json_media_type: str = "application/fake_json"

        assert MyCheckJsonRespPlugin.get_json(
            json_resp({"demo": 1}, content_type="application/fake_json"), pait_context
        ) == {"demo": 1}

    def test_gen_response(self) -> None:
        from sanic.response import json

        from pait.app.sanic.adapter.response import gen_response, gen_unifiled_response
        from pait.model import response

        for gen_method in (gen_response, gen_unifiled_response):
            result = gen_method(json({"demo": 1}), response_model_class=response.BaseResponseModel)
            assert result.body.decode() == '{"demo":1}'

            result = gen_method({"demo": 1}, response_model_class=response.JsonResponseModel)
            assert result.body.decode() == '{"demo":1}'

            class HeaderModel(BaseModel):
                demo: str = Field(alias="x-demo", example="123")

            class MyHtmlResponseModel(response.HtmlResponseModel):
                media_type = "application/demo"
                header = HeaderModel
                status_code = (400,)

            result = gen_method("demo", response_model_class=MyHtmlResponseModel)
            assert result.body.decode() == "demo"
            assert result.content_type == "application/demo"
            assert result.headers == {"x-demo": "123"}
            assert result.status == 400

    def test_simple_route(self, client: SanicTestClient) -> None:
        def simple_route_factory(num: int) -> Callable:
            @pait(response_model_list=[response.HtmlResponseModel])
            def simple_route(request: Request) -> str:
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
        assert client.get("/api/demo/simple-route-1")[1].text == "I'm simple route 1"
        assert client.get("/api/demo/simple-route-2")[1].text == "I'm simple route 2"
        assert client.get("/api/demo/simple-route-2")[1].text == "I'm simple route 2"

    def test_any_type_route(self, base_test: BaseTest) -> None:
        base_test.any_type(main_example.any_type_route)

    def test_tag_route(self, base_test: BaseTest) -> None:
        base_test.tag(main_example.tag_route)

    def test_api_route(self, base_test: BaseTest) -> None:
        from example.sanic_example.api_route import APIRouteCBV, get_user_info, health, login

        base_test.api_route_health(health)
        base_test.api_route_get_user_info(get_user_info)
        base_test.api_route_login(login)
        base_test.api_route_cbv(APIRouteCBV)

    def test_openapi_content(self, base_test: BaseTest) -> None:
        BaseTestOpenAPI(base_test.client.app).test_all()


class TestDocExample:
    def test_hello_world_demo(self) -> None:
        from docs_source_code.introduction import sanic_demo

        with client_ctx(app=sanic_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(sanic_demo.demo_post)

    def test_pait_hello_world_demo(self) -> None:
        from docs_source_code.introduction import sanic_pait_hello_world_demo

        with client_ctx(app=sanic_pait_hello_world_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(sanic_pait_hello_world_demo.demo_post)

    def test_how_to_use_field_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_demo

        with client_ctx(app=sanic_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_demo(sanic_demo.demo_route)

    def test_how_to_use_field_with_default_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_default_demo

        with client_ctx(app=sanic_with_default_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_demo(
                sanic_with_default_demo.demo, sanic_with_default_demo.demo1
            )

    def test_how_to_use_field_with_default_factory_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_default_factory_demo

        with client_ctx(app=sanic_with_default_factory_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_factory_demo(
                sanic_with_default_factory_demo.demo, sanic_with_default_factory_demo.demo1
            )

    def test_how_to_use_field_with_alias_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_alias_demo

        with client_ctx(app=sanic_with_alias_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_alias_demo(sanic_with_alias_demo.demo)

    def test_how_to_use_field_with_number_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_num_check_demo

        with client_ctx(app=sanic_with_num_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_number_verify_demo(
                sanic_with_num_check_demo.demo
            )

    def test_how_to_use_field_with_sequence_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_item_check_demo

        with client_ctx(app=sanic_with_item_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_sequence_verify_demo(
                sanic_with_item_check_demo.demo
            )

    def test_how_to_use_field_with_str_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_string_check_demo

        with client_ctx(app=sanic_with_string_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_str_verify_demo(
                sanic_with_string_check_demo.demo
            )

    def test_how_to_use_field_with_raw_return_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_raw_return_demo

        with client_ctx(app=sanic_with_raw_return_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_raw_return_demo(
                sanic_with_raw_return_demo.demo
            )

    def test_how_to_use_field_with_custom_not_found_exc_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import sanic_with_not_found_exc_demo

        with client_ctx(app=sanic_with_not_found_exc_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_custom_not_found_exc_demo(
                sanic_with_not_found_exc_demo.demo
            )

    def test_how_to_use_type_with_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import sanic_with_model_demo

        with client_ctx(app=sanic_with_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pydantic_basemodel(
                sanic_with_model_demo.demo, sanic_with_model_demo.demo1
            )

    def test_how_to_use_type_with_pait_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import sanic_with_pait_model_demo

        with client_ctx(app=sanic_with_pait_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pait_basemodel(
                sanic_with_pait_model_demo.demo, sanic_with_pait_model_demo.demo1
            )

    def test_how_to_use_type_with_request_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import sanic_with_request_demo

        with client_ctx(app=sanic_with_request_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_request(sanic_with_request_demo.demo)

    def test_how_to_use_type_with_unix_datetime_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import sanic_with_unix_datetime_demo

        with client_ctx(app=sanic_with_unix_datetime_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_customer(
                sanic_with_unix_datetime_demo.demo
            )

    def test_depend_with_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import sanic_with_depend_demo

        with client_ctx(app=sanic_with_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_depend(sanic_with_depend_demo.demo)

    def test_depend_with_nested_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import sanic_with_nested_depend_demo

        with client_ctx(app=sanic_with_nested_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_nested_depend(sanic_with_nested_depend_demo.demo)

    def test_depend_with_context_manager_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import sanic_with_context_manager_depend_demo

        with client_ctx(app=sanic_with_context_manager_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_context_manager_depend(
                sanic_with_context_manager_depend_demo.demo
            )

    def test_depend_with_class_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import sanic_with_class_depend_demo

        with client_ctx(app=sanic_with_class_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_class_depend(sanic_with_class_depend_demo.demo)

    def test_depend_with_pre_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import sanic_with_pre_depend_demo

        with client_ctx(app=sanic_with_pre_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_pre_depend(sanic_with_pre_depend_demo.demo)

    def test_exception_with_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import sanic_with_exception_demo

        with client_ctx(app=sanic_with_exception_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(sanic_with_exception_demo.demo)

    def test_exception_with_not_use_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import sanic_with_not_tip_exception_demo

        with client_ctx(app=sanic_with_not_tip_exception_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(sanic_with_not_tip_exception_demo.demo)

    def test_openapi_security_with_api_key(self) -> None:
        from docs_source_code.openapi.security import sanic_with_apikey_demo

        with client_ctx(app=sanic_with_apikey_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_api_key(
                sanic_with_apikey_demo.api_key_cookie_route,
                sanic_with_apikey_demo.api_key_header_route,
                sanic_with_apikey_demo.api_key_query_route,
            )

    def test_openapi_security_with_http(self) -> None:
        from docs_source_code.openapi.security import sanic_with_http_demo

        with client_ctx(app=sanic_with_http_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_http(
                sanic_with_http_demo.get_user_name_by_http_basic_credentials,
                sanic_with_http_demo.get_user_name_by_http_bearer,
                sanic_with_http_demo.get_user_name_by_http_digest,
            )

    def test_openapi_security_with_oauth2(self) -> None:
        from docs_source_code.openapi.security import sanic_with_oauth2_demo

        with client_ctx(app=sanic_with_oauth2_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_oauth2(
                sanic_with_oauth2_demo.oauth2_login,
                sanic_with_oauth2_demo.oauth2_user_info,
                sanic_with_oauth2_demo.oauth2_user_name,
            )

    def test_plugin_with_required_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import sanic_with_required_plugin_demo

        with client_ctx(app=sanic_with_required_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(sanic_with_required_plugin_demo.demo)

        from docs_source_code.plugin.param_plugin import sanic_with_required_plugin_and_group_extra_param_demo

        with client_ctx(app=sanic_with_required_plugin_and_group_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                sanic_with_required_plugin_and_group_extra_param_demo.demo
            )

        from docs_source_code.plugin.param_plugin import sanic_with_required_plugin_and_extra_param_demo

        with client_ctx(app=sanic_with_required_plugin_and_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                sanic_with_required_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_at_most_of_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import sanic_with_at_most_one_of_plugin_demo

        with client_ctx(app=sanic_with_at_most_one_of_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                sanic_with_at_most_one_of_plugin_demo.demo
            )

        from docs_source_code.plugin.param_plugin import sanic_with_at_most_one_of_plugin_and_extra_param_demo

        with client_ctx(app=sanic_with_at_most_one_of_plugin_and_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                sanic_with_at_most_one_of_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_check_json_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import sanic_with_check_json_plugin_demo

        with client_ctx(app=sanic_with_check_json_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_check_json_response_plugin(
                sanic_with_check_json_plugin_demo.demo
            )

    def test_plugin_with_auto_complete_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import sanic_with_auto_complete_json_plugin_demo

        with client_ctx(app=sanic_with_auto_complete_json_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_auto_complete_json_response_plugin(
                sanic_with_auto_complete_json_plugin_demo.demo
            )

    def test_plugin_with_mock_plugin(self) -> None:
        from docs_source_code.plugin.mock_plugin import sanic_with_mock_plugin_demo

        with client_ctx(app=sanic_with_mock_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_mock_plugin(sanic_with_mock_plugin_demo.demo)

    def test_plugin_with_cache_plugin(self) -> None:
        from docs_source_code.plugin.cache_plugin import sanic_with_cache_plugin_demo

        with client_ctx(app=sanic_with_cache_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_cache_plugin(sanic_with_cache_plugin_demo.demo)
