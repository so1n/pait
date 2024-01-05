import difflib
import json
import random
import sys
from contextlib import contextmanager
from functools import partial
from typing import Callable, Generator, Type
from unittest import mock

import pytest
from flask import Flask, Response
from flask.ctx import AppContext
from flask.testing import FlaskClient
from pydantic import BaseModel, Field
from pytest_mock import MockFixture

from example.common import response_model
from example.flask_example import main_example
from pait.app import auto_load_app
from pait.app.any import get_app_attribute, set_app_attribute
from pait.app.base.simple_route import SimpleRoute
from pait.app.flask import TestHelper as _TestHelper
from pait.app.flask import add_multi_simple_route, add_simple_route, load_app, pait
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
def client_ctx(app: Flask = None) -> Generator[FlaskClient, None, None]:
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    if not app:
        app = main_example.create_app()
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
                ]["get"]["parameters"][0]["example"]
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

    def test_unified_response(self, base_test: BaseTest) -> None:
        base_test.unified_json_response(main_example.unified_json_response)
        base_test.unified_text_response(main_example.unified_text_response)
        base_test.unified_html_response(main_example.unified_html_response)

    def test_check_json_resp_plugin(self, pait_context: ContextModel, base_test: BaseTest) -> None:
        # if not use base_test, flask can not find ctx
        from flask import jsonify

        from pait.app.flask.plugin.check_json_resp import CheckJsonRespPlugin

        assert CheckJsonRespPlugin.get_json(jsonify({"demo": 1}), pait_context) == {"demo": 1}

        with pytest.raises(TypeError):
            CheckJsonRespPlugin.get_json(object, pait_context)

    def test_import_func_from_local_proxy(self, base_test: BaseTest) -> None:
        # if not use base_test, flask can not find ctx
        from flask import current_app

        from pait.app.any.util import import_func_from_app
        from pait.app.flask import pait

        assert import_func_from_app("pait", current_app) == pait

    def test_gen_response(self, base_test: BaseTest) -> None:
        # if not use base_test, flask can not find ctx
        from flask import jsonify

        from pait.app.flask.adapter.response import gen_response
        from pait.model import response

        result = gen_response(jsonify({"demo": 1}), response.BaseResponseModel)
        assert result.json == {"demo": 1}

        result = gen_response({"demo": 1}, response.JsonResponseModel)
        assert result.json == {"demo": 1}

        class HeaderModel(BaseModel):
            demo: str = Field(alias="x-demo", example="123")

        class MyHtmlResponseModel(response.HtmlResponseModel):
            media_type = "application/demo"
            header = HeaderModel
            status_code = (400,)

        result = gen_response("demo", MyHtmlResponseModel)
        assert result.data == b"demo"
        assert result.content_type == "application/demo"
        assert result.headers["x-demo"] == "123"
        assert result.status_code == 400

    def test_simple_route(self, client: FlaskClient) -> None:
        def simple_route_factory(num: int) -> Callable:
            @pait(response_model_list=[response.HtmlResponseModel])
            def simple_route() -> str:
                return f"I'm simple route {num}"

            simple_route.__name__ = simple_route.__name__ + str(num)
            return simple_route

        add_simple_route(
            client.application,
            SimpleRoute(methods=["GET"], url="/api/demo/simple-route-1", route=simple_route_factory(1)),
        )
        add_multi_simple_route(
            client.application,
            SimpleRoute(methods=["GET"], url="/demo/simple-route-2", route=simple_route_factory(2)),
            SimpleRoute(methods=["GET"], url="/demo/simple-route-3", route=simple_route_factory(3)),
            prefix="/api",
            title="test",
        )
        assert client.get("/api/demo/simple-route-1").data == b"I'm simple route 1"
        assert client.get("/api/demo/simple-route-2").data == b"I'm simple route 2"
        assert client.get("/api/demo/simple-route-2").data == b"I'm simple route 2"

    def test_any_type_route(self, base_test: BaseTest) -> None:
        base_test.any_type(main_example.any_type_route)

    def test_tag_route(self, base_test: BaseTest) -> None:
        base_test.tag(main_example.tag_route)

    def test_openapi_content(self, base_test: BaseTest) -> None:
        BaseTestOpenAPI(base_test.client.application).test_all()


class TestFlaskExtra:
    def test_test_helper_form_dict_have_file_dict(self, base_test: BaseTest) -> None:
        from pait.app.base import BaseAppHelper
        from pait.model.core import PaitCoreModel
        from pait.param_handle import ParamHandler

        def demo() -> None:
            pass

        core_model = PaitCoreModel(demo, app_helper_class=BaseAppHelper, param_handler_plugin=ParamHandler)

        test_helper = _TestHelper(
            base_test.client, demo, pait_dict={core_model.pait_id: core_model}, form_dict={"a": 1}, file_dict={"b": 2}
        )
        assert test_helper.form_dict == {"a": 1, "b": 2}
        test_helper = _TestHelper(
            base_test.client, demo, pait_dict={core_model.pait_id: core_model}, file_dict={"b": 2}
        )
        assert test_helper.form_dict == {"b": 2}


class TestDocExample:
    def test_hello_world_demo(self) -> None:
        from docs_source_code.introduction import flask_demo

        with client_ctx(app=flask_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(flask_demo.demo_post)

    def test_pait_hello_world_demo(self) -> None:
        from docs_source_code.introduction import flask_pait_hello_world_demo

        with client_ctx(app=flask_pait_hello_world_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(flask_pait_hello_world_demo.demo_post)

    def test_how_to_use_field_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_demo

        with client_ctx(app=flask_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_demo(flask_demo.demo_route)

    def test_how_to_use_field_with_default_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_default_demo

        with client_ctx(app=flask_with_default_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_demo(
                flask_with_default_demo.demo, flask_with_default_demo.demo1
            )

    def test_how_to_use_field_with_default_factory_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_default_factory_demo

        with client_ctx(app=flask_with_default_factory_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_factory_demo(
                flask_with_default_factory_demo.demo, flask_with_default_factory_demo.demo1
            )

    def test_how_to_use_field_with_alias_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_alias_demo

        with client_ctx(app=flask_with_alias_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_alias_demo(flask_with_alias_demo.demo)

    def test_how_to_use_field_with_number_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_num_check_demo

        with client_ctx(app=flask_with_num_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_number_verify_demo(
                flask_with_num_check_demo.demo
            )

    def test_how_to_use_field_with_sequence_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_item_check_demo

        with client_ctx(app=flask_with_item_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_sequence_verify_demo(
                flask_with_item_check_demo.demo
            )

    def test_how_to_use_field_with_str_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_string_check_demo

        with client_ctx(app=flask_with_string_check_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_str_verify_demo(
                flask_with_string_check_demo.demo
            )

    def test_how_to_use_field_with_raw_return_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_raw_return_demo

        with client_ctx(app=flask_with_raw_return_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_raw_return_demo(
                flask_with_raw_return_demo.demo
            )

    def test_how_to_use_field_with_custom_not_found_exc_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import flask_with_not_found_exc_demo

        with client_ctx(app=flask_with_not_found_exc_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_custom_not_found_exc_demo(
                flask_with_not_found_exc_demo.demo
            )

    def test_how_to_use_type_with_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import flask_with_model_demo

        with client_ctx(app=flask_with_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pydantic_basemodel(
                flask_with_model_demo.demo, flask_with_model_demo.demo1
            )

    def test_how_to_use_type_with_pait_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import flask_with_pait_model_demo

        with client_ctx(app=flask_with_pait_model_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pait_basemodel(
                flask_with_pait_model_demo.demo, flask_with_pait_model_demo.demo1
            )

    def test_how_to_use_type_with_request_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import flask_with_request_demo

        with client_ctx(app=flask_with_request_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_request(flask_with_request_demo.demo)

    def test_how_to_use_type_with_unix_datetime_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import flask_with_unix_datetime_demo

        with client_ctx(app=flask_with_unix_datetime_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_customer(
                flask_with_unix_datetime_demo.demo
            )

    def test_depend_with_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import flask_with_depend_demo

        with client_ctx(app=flask_with_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_depend(flask_with_depend_demo.demo)

    def test_depend_with_nested_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import flask_with_nested_depend_demo

        with client_ctx(app=flask_with_nested_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_nested_depend(flask_with_nested_depend_demo.demo)

    def test_depend_with_context_manager_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import flask_with_context_manager_depend_demo

        with client_ctx(app=flask_with_context_manager_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_context_manager_depend(
                flask_with_context_manager_depend_demo.demo
            )

    def test_depend_with_class_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import flask_with_class_depend_demo

        with client_ctx(app=flask_with_class_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_class_depend(flask_with_class_depend_demo.demo)

    def test_depend_with_pre_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import flask_with_pre_depend_demo

        with client_ctx(app=flask_with_pre_depend_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_pre_depend(flask_with_pre_depend_demo.demo)

    def test_exception_with_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import flask_with_exception_demo

        with client_ctx(app=flask_with_exception_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(flask_with_exception_demo.demo)

    def test_exception_with_not_use_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import flask_with_not_tip_exception_demo

        with client_ctx(app=flask_with_not_tip_exception_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(flask_with_not_tip_exception_demo.demo)

    def test_openapi_security_with_api_key(self) -> None:
        from docs_source_code.openapi.security import flask_with_apikey_demo

        with client_ctx(app=flask_with_apikey_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_api_key(
                flask_with_apikey_demo.api_key_cookie_route,
                flask_with_apikey_demo.api_key_header_route,
                flask_with_apikey_demo.api_key_query_route,
            )

    def test_openapi_security_with_http(self) -> None:
        from docs_source_code.openapi.security import flask_with_http_demo

        with client_ctx(app=flask_with_http_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_http(
                flask_with_http_demo.get_user_name_by_http_basic_credentials,
                flask_with_http_demo.get_user_name_by_http_bearer,
                flask_with_http_demo.get_user_name_by_http_digest,
            )

    def test_openapi_security_with_oauth2(self) -> None:
        from docs_source_code.openapi.security import flask_with_oauth2_demo

        with client_ctx(app=flask_with_oauth2_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_oauth2(
                flask_with_oauth2_demo.oauth2_login,
                flask_with_oauth2_demo.oauth2_user_info,
                flask_with_oauth2_demo.oauth2_user_name,
            )

    def test_plugin_with_required_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            flask_with_required_plugin_and_extra_param_demo,
            flask_with_required_plugin_and_group_extra_param_demo,
            flask_with_required_plugin_demo,
        )

        with client_ctx(app=flask_with_required_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(flask_with_required_plugin_demo.demo)
        with client_ctx(app=flask_with_required_plugin_and_group_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                flask_with_required_plugin_and_group_extra_param_demo.demo
            )
        with client_ctx(app=flask_with_required_plugin_and_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                flask_with_required_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_at_most_of_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            flask_with_at_most_one_of_plugin_and_extra_param_demo,
            flask_with_at_most_one_of_plugin_demo,
        )

        with client_ctx(app=flask_with_at_most_one_of_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                flask_with_at_most_one_of_plugin_demo.demo
            )
        with client_ctx(app=flask_with_at_most_one_of_plugin_and_extra_param_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                flask_with_at_most_one_of_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_check_json_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import flask_with_check_json_plugin_demo

        with client_ctx(app=flask_with_check_json_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_check_json_response_plugin(
                flask_with_check_json_plugin_demo.demo
            )

    def test_plugin_with_auto_complete_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import flask_with_auto_complete_json_plugin_demo

        with client_ctx(app=flask_with_auto_complete_json_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_auto_complete_json_response_plugin(
                flask_with_auto_complete_json_plugin_demo.demo
            )

    def test_plugin_with_mock_plugin(self) -> None:
        from docs_source_code.plugin.mock_plugin import flask_with_mock_plugin_demo

        with client_ctx(app=flask_with_mock_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_mock_plugin(flask_with_mock_plugin_demo.demo)

    def test_plugin_with_cache_plugin(self) -> None:
        from docs_source_code.plugin.cache_plugin import flask_with_cache_plugin_demo

        with client_ctx(app=flask_with_cache_plugin_demo.app) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_cache_plugin(flask_with_cache_plugin_demo.demo)
