import difflib
import json
import random
import sys
from functools import partial
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Type
from unittest import mock

import pytest
from redis import Redis  # type: ignore
from tornado.testing import AsyncHTTPTestCase, HTTPResponse
from tornado.web import Application

from example.tornado_example import main_example
from pait.app import auto_load_app
from pait.app.any import get_app_attribute, set_app_attribute
from pait.app.base.simple_route import SimpleRoute
from pait.app.tornado import TestHelper as _TestHelper
from pait.app.tornado import add_multi_simple_route, add_simple_route, load_app, pait
from pait.model import response
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
    _TestHelper, load_app=partial(load_app, overwrite_already_exists_data=True)
)


class BaseTestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return main_example.create_app()

    @property
    def base_test(self) -> BaseTest:
        return BaseTest(self, _TestHelper)

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)


class TestTornado(BaseTestTornado):
    def response_test_helper(self, route_handler: Callable, pait_response: Type[response.BaseResponseModel]) -> None:
        from pait.app.tornado.plugin.mock_response import MockPlugin

        test_helper: _TestHelper = _TestHelper(self, route_handler)
        test_helper.get()

        with enable_plugin(route_handler, MockPlugin.build()):
            resp: HTTPResponse = test_helper.get()
            for key, value in pait_response.get_header_example_dict().items():
                assert resp.headers[key] == value
            if issubclass(pait_response, response.HtmlResponseModel) or issubclass(
                pait_response, response.TextResponseModel
            ):
                assert resp.body.decode() == pait_response.get_example_value()
            else:
                assert resp.body == pait_response.get_example_value()

    def test_post(self) -> None:
        test_helper: _TestHelper = _TestHelper(
            self,
            main_example.PostHandler.post,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        response: HTTPResponse = self.fetch(
            "/api/field/post",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}',
        )
        for resp_dict in [test_helper.json(), json.loads(response.body.decode())]:
            assert resp_dict["code"] == 0
            assert resp_dict["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/x-www-form-urlencoded",
                "sex": "man",
            }

    def test_check_json_route(self) -> None:
        for url, api_code in [
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10", -1),
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = json.loads(self.fetch(url).body.decode())
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_text_response(self) -> None:
        self.response_test_helper(main_example.TextResponseHanler.get, response.TextResponseModel)

    def test_html_response(self) -> None:
        self.response_test_helper(main_example.HtmlResponseHanler.get, response.HtmlResponseModel)

    def test_file_response(self) -> None:
        self.response_test_helper(main_example.FileResponseHanler.get, response.FileResponseModel)

    def test_doc_route(self) -> None:
        main_example.add_api_doc_route(self._app)
        for doc_route_path in default_doc_fn_dict.keys():
            assert self.fetch(f"/{doc_route_path}").code == 404
            assert self.fetch(f"/api-doc/{doc_route_path}").code == 200

        for doc_route_path, fn in default_doc_fn_dict.items():
            assert self.fetch(f"/{doc_route_path}?pin-code=6666").body.decode() == fn(
                self.get_url("/openapi.json?pin-code=6666"), title="Pait Api Doc(private)"
            )

        assert (
            difflib.SequenceMatcher(
                None,
                self.fetch("/openapi.json?pin-code=6666").body.decode(),
                OpenAPI(
                    self._app,
                    openapi_info_model=InfoModel(title="Pait Doc"),
                    server_model_list=[ServerModel(url="http://localhost")],
                ).content(),
            ).quick_ratio()
            > 0.95
        )

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import tornado

        with mock.patch.dict("sys.modules", sys.modules):
            assert tornado == auto_load_app.auto_load_app_class()

    def test_app_attribute(self) -> None:
        key: str = "test_app_attribute"
        value: int = random.randint(1, 100)
        app: Application = self.get_app()
        set_app_attribute(app, key, value)
        assert get_app_attribute(app, key) == value

    def test_pait_base_field_route(self) -> None:
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
                    "form_c": ["3"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == _TestHelper(
                self,
                main_example.PaitBaseFieldHandler.post,
                file_dict={f1.name: f1.read()},
                form_dict={"a": "1", "b": 2, "c": "3"},
                cookie_dict={"abcd": "abcd"},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

            # can not use get(Http Method) in form or file request
            with pytest.raises(RuntimeError):
                _TestHelper(
                    self,
                    main_example.PaitBaseFieldHandler.post,
                    file_dict={f1.name: f1.read()},
                    form_dict={"a": "1", "b": "2", "c": "3"},
                    cookie_dict={"cookie": "abcd=abcd;"},
                    query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                    path_dict={"age": 2},
                    strict_inspection_check_json_content=False,
                ).get()

    @mock.patch("pait.util._gen_tip.logging.debug")
    def test_raise_tip_route(self, debug_logger: Any) -> None:
        self.base_test.raise_tip_route(main_example.RaiseTipHandler.post, debug_logger=debug_logger)

    @mock.patch("pait.util._gen_tip.logging.debug")
    def test_raise_not_tip_route(self, debug_logger: Any) -> None:
        self.base_test.raise_tip_route(main_example.RaiseNotTipHandler.post, debug_logger=debug_logger, is_raise=False)

    @mock.patch("pait.util._gen_tip.logging.debug")
    def test_new_raise_not_tip_route(self, debug_logger: Any) -> None:
        self.base_test.raise_tip_route(
            main_example.NewRaiseNotTipHandler.post, debug_logger=debug_logger, is_raise=False
        )

    def test_auto_complete_json_route(self) -> None:
        self.base_test.auto_complete_json_route(main_example.AutoCompleteJsonHandler.get)

    def test_same_alias_name(self) -> None:
        self.base_test.same_alias_name(main_example.SameAliasHandler.get)

    def test_field_default_factory_route(self) -> None:
        self.base_test.field_default_factory_route(main_example.FieldDefaultFactoryHandler.post)

    def test_param_at_most_one_of_route(self) -> None:
        self.base_test.param_at_most_one_of_route(main_example.ParamAtMostOneOfByExtraParamHandler.get)
        self.base_test.param_at_most_one_of_route(main_example.ParamAtMostOneOfHandler.get)

    def test_param_required_route(self) -> None:
        self.base_test.param_required_route(main_example.ParamRequiredHandler.get)
        self.base_test.param_required_route(main_example.ParamRequiredByExtraParamHandler.get)

    def test_check_response(self) -> None:
        self.base_test.check_response(main_example.CheckRespHandler.get)

    def test_mock_route(self) -> None:
        self.base_test.mock_route(main_example.MockHandler.get)

    def test_pait_model(self) -> None:
        self.base_test.pait_model(main_example.PaitModelHandler.post)

    def test_depend_route(self) -> None:
        self.base_test.depend_route(main_example.DependHandler.post)

    def test_pre_depend_route(self) -> None:
        self.base_test.pre_depend_route(main_example.PreDependHandler.post)

    @mock.patch("example.common.depend.logging.error")
    @mock.patch("example.common.depend.logging.info")
    def test_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.depend_contextmanager(
            main_example.DependContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.common.depend.logging.error")
    @mock.patch("example.common.depend.logging.info")
    def test_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.depend_contextmanager(
            main_example.DependAsyncContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.common.depend.logging.error")
    @mock.patch("example.common.depend.logging.info")
    def test_pre_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.pre_depend_contextmanager(
            main_example.PreDependContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("example.common.depend.logging.error")
    @mock.patch("example.common.depend.logging.info")
    def test_pre_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        self.base_test.pre_depend_contextmanager(
            main_example.PreDependAsyncContextmanagerHanler.get,
            info_logger=info_logger,
            error_logger=error_logger,
        )

    @mock.patch("asyncio.log.logger.warning")
    def test_sync_to_thread(self, logger: Any) -> None:
        self.base_test.base_sync_depend_route(
            main_example.SyncDependHandler.post, {"body_dict": {"uid": 10086, "name": "so1n"}}
        )
        self.base_test.base_sync_depend_route(
            main_example.SyncToThreadBodyHandler.post, {"body_dict": {"uid": 10086, "name": "so1n"}}
        )
        self.base_test.base_sync_depend_route(
            main_example.SyncWithCtxDependHandler.post, {"body_dict": {"uid": 10086, "name": "so1n"}}
        )
        # if call_args is not None, a blocking function is encountered
        assert logger.call_args is None

    def test_api_key_route(self) -> None:
        self.base_test.api_key_route(main_example.APIKeyCookieHandler.get, {"cookie_dict": {"token": "my-token"}})
        self.base_test.api_key_route(main_example.APIKeyHeaderHandler.get, {"header_dict": {"token": "my-token"}})
        self.base_test.api_key_route(main_example.APIKeyQueryHandler.get, {"query_dict": {"token": "my-token"}})

    def test_oauth2_password_route(self) -> None:
        self.base_test.oauth2_password_route(
            login_route=main_example.OAuth2LoginHandler.post,
            user_name_route=main_example.OAuth2UserNameHandler.get,
            user_info_route=main_example.OAuth2UserInfoHandler.get,
        )

    def test_get_user_name_by_http_bearer(self) -> None:
        self.base_test.get_user_name_by_http_bearer(main_example.UserNameByHttpBearerHandler.get)

    def test_get_user_name_by_http_digest(self) -> None:
        self.base_test.get_user_name_by_http_digest(main_example.UserNameByHttpDigestHandler.get)

    def test_get_user_name_by_http_basic_credentials(self) -> None:
        self.base_test.get_user_name_by_http_basic_credentials(main_example.UserNameByHttpBasicCredentialsHandler.get)

    def test_get_cbv(self) -> None:
        self.base_test.get_cbv(main_example.CbvHandler.get)

    def test_post_cbv(self) -> None:
        self.base_test.post_cbv(main_example.CbvHandler.post)

    def test_cache_response(self) -> None:
        self.base_test.cache_response(
            main_example.CacheResponseHandler.get,
            main_example.CacheResponse1Handler.get,
            key="CacheResponse",
            app="tornado",
        )

    def test_cache_other_response_type(self) -> None:
        main_example.CacheResponsePlugin.set_redis_to_app(self._app, main_example.Redis(decode_responses=True))
        self.base_test.cache_other_response_type(
            main_example.TextResponseHanler.get,
            main_example.HtmlResponseHanler.get,
            main_example.CacheResponsePlugin,
        )

    def test_cache_response_param_name(self) -> None:
        self.base_test.cache_response_param_name(
            main_example.PostHandler.post,
            main_example.CacheResponsePlugin,
            main_example.Redis(decode_responses=True),
        )

    def test_unified_response(self) -> None:
        self.base_test.unified_json_response(main_example.UnifiedJsonResponseHandler.get)
        self.base_test.unified_text_response(main_example.UnifiedTextResponseHandler.get)
        self.base_test.unified_html_response(main_example.UnifiedHtmlResponseHandler.get)

    def test_check_json_resp_plugin(self) -> None:
        pass

        # TODO The Tornado test is more complicated and will be ignored for now

    def test_gen_response(self) -> None:
        # TODO The Tornado test is more complicated and will be ignored for now
        pass

    def test_simple_route(self) -> None:
        def simple_route_factory(num: int) -> Callable:
            @pait(response_model_list=[response.HtmlResponseModel])
            def simple_route() -> str:
                return f"I'm simple route {num}"

            simple_route.__name__ = simple_route.__name__ + str(num)
            return simple_route

        add_simple_route(
            self._app, SimpleRoute(methods=["GET"], url="/api/demo/simple-route-1", route=simple_route_factory(1))
        )
        add_multi_simple_route(
            self._app,
            SimpleRoute(methods=["GET"], url="/demo/simple-route-2", route=simple_route_factory(2)),
            SimpleRoute(methods=["GET"], url="/demo/simple-route-3", route=simple_route_factory(3)),
            prefix="/api",
            title="test",
        )
        assert self.fetch("/api/demo/simple-route-1").body.decode() == "I'm simple route 1"
        assert self.fetch("/api/demo/simple-route-2").body.decode() == "I'm simple route 2"
        assert self.fetch("/api/demo/simple-route-2").body.decode() == "I'm simple route 2"

    def test_any_type_route(self) -> None:
        self.base_test.any_type(main_example.AnyTypeHandler.post)

    def test_tag_route(self) -> None:
        self.base_test.tag(main_example.TagHandler.get)

    def test_api_route(self) -> None:
        from example.tornado_example.api_route import APIRouteCBVHandler, get_user_info, health, login

        self.base_test.api_route_health(health)
        self.base_test.api_route_get_user_info(get_user_info)
        self.base_test.api_route_login(login)
        self.base_test.api_route_cbv(APIRouteCBVHandler)

    def test_openapi_content(self) -> None:
        BaseTestOpenAPI(self._app).test_all()


class BaseTestTornadoDocExample(BaseTestTornado):
    demo: Any

    def get_app(self) -> Application:
        return self.demo.app


class TestDocHelloWorldExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction import tornado_demo

    demo = tornado_demo

    def test_hello_world_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).hello_world_demo(self.demo.DemoHandler.post)


class TestDocPaitHelloWorldExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction import tornado_pait_hello_world_demo

    demo = tornado_pait_hello_world_demo

    def test_hello_world_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).hello_world_demo(self.demo.DemoHandler.post)


class TestDocHowToUseFieldExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_demo

    demo = tornado_demo

    def test_how_to_use_field_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_demo(self.demo.DemoHandler.post)


class TestDocHowToUseFieldWithDefaultExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_default_demo

    demo = tornado_with_default_demo

    def test_how_to_use_field_with_default_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_default_demo(
            self.demo.DemoHandler.get, self.demo.Demo1Handler.get
        )


class TestDocHowToUseFieldWithDefaultFactoryExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_default_factory_demo

    demo = tornado_with_default_factory_demo

    def test_how_to_use_field_with_default_factory_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_default_factory_demo(
            self.demo.DemoHandler.get, self.demo.Demo1Handler.get
        )


class TestDocHowToUseFieldWithAliasExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_alias_demo

    demo = tornado_with_alias_demo

    def test_how_to_use_field_with_alias_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_alias_demo(
            self.tornado_with_alias_demo.DemoHandler.get
        )


class TestDocHowToUseFieldWithNumberVerifyExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_num_check_demo

    demo = tornado_with_num_check_demo

    def test_how_to_use_field_with_number_verify_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_number_verify_demo(self.demo.DemoHandler.get)


class TestDocHowToUseFieldWithStrVerifyExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_string_check_demo

    demo = tornado_with_string_check_demo

    def test_how_to_use_field_with_str_verify_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_str_verify_demo(self.demo.DemoHandler.get)


class TestDocHowToUseFieldWithRawReturnExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_raw_return_demo

    demo = tornado_with_raw_return_demo

    def test_how_to_use_field_with_raw_return_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_raw_return_demo(self.demo.DemoHandler.post)


class TestDocHowToUseFieldWithCustomNotFoundExcExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_field import tornado_with_not_found_exc_demo

    demo = tornado_with_not_found_exc_demo

    def test_how_to_use_field_with_custom_not_found_exc_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_field_with_custom_not_found_exc_demo(self.demo.DemoHandler.get)


class TestDocHowToUseTypeWithModelExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_type import tornado_with_model_demo

    demo = tornado_with_model_demo

    def test_how_to_use_type_with_model_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_type_with_type_is_pydantic_basemodel(
            self.demo.DemoHandler.get, self.demo.Demo1Handler.post
        )


class TestDocHowToUseTypeWithPaitModelExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_type import tornado_with_pait_model_demo

    demo = tornado_with_pait_model_demo

    def test_how_to_use_type_with_pait_model_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_type_with_type_is_pait_basemodel(
            self.demo.DemoHandler.get, self.demo.Demo1Handler.post
        )


class TestDocHowToUseTypeWithRequestExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_type import tornado_with_request_demo

    demo = tornado_with_request_demo

    def test_how_to_use_type_with_request_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_type_with_type_is_request(self.demo.DemoHandler.get)


class TestDocHowToUseTypeWithUnixDatetimeExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.how_to_use_type import tornado_with_unix_datetime_demo

    demo = tornado_with_unix_datetime_demo

    def test_how_to_use_type_with_unix_datetime_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).how_to_use_type_with_type_is_customer(self.demo.DemoHandler.get)


class TestDocWithDependExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.depend import tornado_with_depend_demo

    demo = tornado_with_depend_demo

    def test_depend_with_depend_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_depend(self.demo.DemoHandler.get)


class TestDocWithNestedDependExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.depend import tornado_with_nested_depend_demo

    demo = tornado_with_nested_depend_demo

    def test_depend_with_nested_depend_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_nested_depend(self.demo.DemoHandler.get)


class TestDocWithContextManagerDependExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.depend import tornado_with_context_manager_depend_demo

    demo = tornado_with_context_manager_depend_demo

    def test_depend_with_context_manager_depend_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_context_manager_depend(self.demo.DemoHandler.get)


class TestDocTypeWithClassDependExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.depend import tornado_with_class_depend_demo

    demo = tornado_with_class_depend_demo

    def test_depend_with_class_depend_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_class_depend(self.demo.DemoHandler.get)


class TestDocWithPreDependExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.depend import tornado_with_pre_depend_demo

    demo = tornado_with_pre_depend_demo

    def test_depend_with_pre_depend_demo(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_pre_depend(self.demo.DemoHandler.get)


class TestDocWithExceptionTipExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.exception import tornado_with_exception_demo

    demo = tornado_with_exception_demo

    def test_exception_with_exception_tip(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_exception_tip(self.demo.DemoHandler.get)


class TestDocWithNotUseExceptionTipExample(BaseTestTornadoDocExample):
    from docs_source_code.introduction.exception import tornado_with_not_tip_exception_demo

    demo = tornado_with_not_tip_exception_demo

    def test_exception_with_not_use_exception_tip(self) -> None:
        BaseTestDocExample(self, _TestHelper).with_exception_tip(self.demo.DemoHandler.get)


class TestDocOpenApiSecurityWithApiKeyExample(BaseTestTornadoDocExample):
    from docs_source_code.openapi.security import tornado_with_apikey_demo

    demo = tornado_with_apikey_demo

    def test_openapi_security_with_api_key(self) -> None:
        BaseTestDocExample(self, _TestHelper).openapi_security_with_api_key(
            self.demo.APIKeyCookieHandler.get,
            self.demo.APIKeyHeaderHandler.get,
            self.demo.APIKeyQueryHandler.get,
        )


class TestDocOpenApiSecurityWithOauth2Example(BaseTestTornadoDocExample):
    from docs_source_code.openapi.security import tornado_with_oauth2_demo

    demo = tornado_with_oauth2_demo

    def test_openapi_security_with_oauth2(self) -> None:
        BaseTestDocExample(self, _TestHelper).openapi_security_with_oauth2(
            self.demo.OAuth2LoginHandler.post,
            self.demo.OAuth2UserInfoHandler.get,
            self.demo.OAuth2UserNameHandler.get,
        )


class TestDocPluginWithRequiredPluginExample1(BaseTestTornadoDocExample):
    from docs_source_code.plugin.param_plugin import tornado_with_required_plugin_demo

    demo = tornado_with_required_plugin_demo

    def test_plugin_with_required_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_required_plugin(self.demo.DemoHandler.get)


class TestDocPluginWithRequiredPluginExample2(TestDocPluginWithRequiredPluginExample1):
    from docs_source_code.plugin.param_plugin import tornado_with_required_plugin_and_extra_param_demo

    demo = tornado_with_required_plugin_and_extra_param_demo


class TestDocPluginWithRequiredPluginExample3(TestDocPluginWithRequiredPluginExample1):
    from docs_source_code.plugin.param_plugin import tornado_with_required_plugin_and_group_extra_param_demo

    demo = tornado_with_required_plugin_and_group_extra_param_demo


class TestDocPluginAtMostOfPluginExample1(BaseTestTornadoDocExample):
    from docs_source_code.plugin.param_plugin import tornado_with_at_most_one_of_plugin_demo

    demo = tornado_with_at_most_one_of_plugin_demo

    def test_plugin_with_at_most_of_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_at_most_one_of_plugin(self.demo.DemoHandler.get)


class TestDocPluginAtMostOfPluginExample2(TestDocPluginAtMostOfPluginExample1):
    from docs_source_code.plugin.param_plugin import tornado_with_at_most_one_of_plugin_demo

    demo = tornado_with_at_most_one_of_plugin_demo


class TestDocPluginWithCheckJsonPluginExample(BaseTestTornadoDocExample):
    from docs_source_code.plugin.json_plugin import tornado_with_check_json_plugin_demo

    demo = tornado_with_check_json_plugin_demo

    def test_plugin_with_check_json_response_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_check_json_response_plugin(self.demo.DemoHandler.get)


class TestDocPluginWithAutoCompletePluginExample(BaseTestTornadoDocExample):
    from docs_source_code.plugin.json_plugin import tornado_with_auto_complete_json_plugin_demo

    demo = tornado_with_auto_complete_json_plugin_demo

    def test_plugin_with_auto_complete_response_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_auto_complete_json_response_plugin(self.demo.DemoHandler.get)


class TestDocPluginWithMockPluginExample(BaseTestTornadoDocExample):
    from docs_source_code.plugin.mock_plugin import tornado_with_mock_plugin_demo

    demo = tornado_with_mock_plugin_demo

    def test_plugin_with_mock_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_mock_plugin(self.demo.DemoHandler.get)


class TestDocPluginWithCachePluginExample(BaseTestTornadoDocExample):
    from docs_source_code.plugin.cache_plugin import tornado_with_cache_plugin_demo

    demo = tornado_with_cache_plugin_demo

    def test_plugin_with_cache_plugin(self) -> None:
        BaseTestDocExample(self, _TestHelper).plugin_with_cache_plugin(self.demo.DemoHandler.get)
