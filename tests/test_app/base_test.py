from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

import pytest
from pytest_mock import MockFixture
from redis import Redis  # type: ignore

from example.param_verify.model import gen_response_model_handle
from pait.app.base import BaseTestHelper
from pait.app.base.grpc_route import BaseGrpcGatewayRoute
from pait.model.response import BaseResponseModel, HtmlResponseModel, TextResponseModel
from pait.plugin.cache_response import CacheResponsePlugin
from tests.conftest import enable_plugin, grpc_test_openapi

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class BaseTest(object):
    def __init__(self, client: Any, test_helper: Type[BaseTestHelper]):
        self.client: Any = client
        self.test_helper: Type[BaseTestHelper] = test_helper

    def raise_tip_route(self, route: Callable) -> None:
        msg: str = self.test_helper(
            self.client, route, header_dict={"Content-Type": "test"}, body_dict={"temp": None}
        ).json()["msg"]
        assert msg == "error param:content__type, Can not found content__type value"

    def auto_complete_json_route(self, route: Callable) -> None:
        test_helper: BaseTestHelper = self.test_helper(self.client, route)
        resp_dict: dict = test_helper.json()
        assert resp_dict["data"]["uid"] == 100
        assert resp_dict["data"]["music_list"][1]["name"] == ""
        assert resp_dict["data"]["music_list"][1]["singer"] == ""

    def depend_route(self, route: Callable) -> None:
        assert {"code": 0, "msg": "", "data": {"age": 2, "user_agent": "customer_agent"}} == self.test_helper(
            self.client,
            route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json()

    def same_alias_name(self, route: Callable) -> None:
        assert (
            self.test_helper(
                self.client,
                route,
                query_dict={"token": "query"},
                header_dict={"token": "header"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        )
        assert (
            self.test_helper(
                self.client,
                route,
                query_dict={"token": "query1"},
                header_dict={"token": "header1"},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}
        )

    def field_default_factory_route(self, route: Callable) -> None:
        assert (
            self.test_helper(
                self.client,
                route,
                body_dict={"demo_value": 0},
                strict_inspection_check_json_content=False,
            ).json()
            == {"code": 0, "msg": "", "data": {"demo_value": 0, "data_list": [], "data_dict": {}}}
        )

    def pait_base_field_route(self, route: Callable, ignore_path: bool = True) -> None:
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
                    "filename": f1.name.split("/")[-1] if ignore_path else f1.name,
                    "form_a": "1",
                    "form_b": "2",
                    "form_c": ["3", "4"],
                    "multi_user_name": ["abc", "efg"],
                    "sex": "man",
                    "uid": 123,
                    "user_name": "appl",
                },
                "msg": "",
            } == self.test_helper(
                self.client,
                route,
                file_dict={"upload_file": f1},
                cookie_dict={"abcd": "abcd"},
                form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                path_dict={"age": 2},
                strict_inspection_check_json_content=False,
            ).json()

    def check_param(self, route: Callable) -> None:
        test_helper: BaseTestHelper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert "birthday requires param alias_user_name, which if not none" in test_helper.json()["msg"]
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "sex": "man", "age": 10, "birthday": "2000-01-01", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert test_helper.json()["code"] == 0

    def check_response(self, route: Callable) -> None:
        test_helper: BaseTestHelper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.json()
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def mock_route(self, route: Callable, resp_model: Type[BaseResponseModel]) -> None:
        assert (
            self.test_helper(
                self.client,
                route,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == resp_model.get_example_value()
        )

    def pait_model(self, route: Callable) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {
                "uid": 123,
                "user_agent": "customer_agent",
                "user_info": {"age": 2, "user_name": "appl"},
            },
        } == self.test_helper(
            self.client,
            route,
            header_dict={"user-agent": "customer_agent"},
            query_dict={"uid": 123, "user_name": "appl"},
            body_dict={"user_info": {"age": 2, "user_name": "appl"}},
            strict_inspection_check_json_content=False,
        ).json()

    def depend_contextmanager(
        self, route: Callable, mocker: Optional[MockFixture] = None, error_logger: Any = None, info_logger: Any = None
    ) -> None:
        if mocker:
            error_logger = mocker.patch("example.param_verify.model.logging.error")
            info_logger = mocker.patch("example.param_verify.model.logging.info")
        else:
            if not error_logger or not info_logger:
                raise RuntimeError("mocker or error_logger and info_logger must be not None")
        self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123},
        ).get()
        info_logger.assert_called_once_with("context_depend exit")
        self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "is_raise": True},
        ).get()
        error_logger.assert_called_once_with("context_depend error")

    def pre_depend_contextmanager(
        self, route: Callable, mocker: Optional[MockFixture] = None, error_logger: Any = None, info_logger: Any = None
    ) -> None:
        if mocker:
            error_logger = mocker.patch("example.param_verify.model.logging.error")
            info_logger = mocker.patch("example.param_verify.model.logging.info")
        else:
            if not error_logger or not info_logger:
                raise RuntimeError("mocker or error_logger and info_logger must be not None")
        self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123},
        ).get()
        info_logger.assert_called_once_with("context_depend exit")
        self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "is_raise": True},
        ).get()
        error_logger.assert_called_once_with("context_depend error")

    def get_cbv(self, route: Callable) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == self.test_helper(
            self.client,
            route,
            query_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def post_cbv(self, route: Callable) -> None:
        assert {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "appl", "sex": "man", "age": 2, "content_type": "application/json"},
        } == self.test_helper(
            self.client,
            route,
            body_dict={"uid": "123", "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"Content-Type": "application/json"},
        ).json()

    def cache_response(
        self,
        cache_response: Callable,
        cache_response1: Callable,
        key: str = "cache_response",
        app: str = "",
    ) -> None:
        def del_key(key: str) -> None:
            redis: Redis = Redis()
            for _key in redis.scan_iter(match=key + "*"):
                redis.delete(_key)

        # test not exc
        del_key(key)
        result1: str = self.test_helper(self.client, cache_response).text()
        result2: str = self.test_helper(self.client, cache_response).text()
        result3: str = self.test_helper(self.client, cache_response1).text()
        result4: str = self.test_helper(self.client, cache_response1).text()
        assert result1 == result2
        assert result3 == result4
        assert result1 != result3
        assert result2 != result4
        del_key(key)
        assert result1 != self.test_helper(self.client, cache_response).text()
        assert result3 != self.test_helper(self.client, cache_response1).text()

        # test not include exc
        del_key(key)
        if not app:
            with pytest.raises(RuntimeError) as e:
                self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).text()

                exec_msg: str = e.value.args[0]
                assert "'status_code': 500" in exec_msg
        elif app == "starlette":
            with pytest.raises(Exception):
                self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).text()
        elif app == "tornado":
            assert self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).json()["code"] == -1

        # test include exc
        del_key("cache_response")
        result_5 = self.test_helper(self.client, cache_response, query_dict={"raise_exc": 2}).text()
        result_6 = self.test_helper(self.client, cache_response, query_dict={"raise_exc": 2}).text()
        assert result_5 == result_6

    def cache_other_response_type(
        self, text_route: Callable, html_route: Callable, cache_plugin: Type[CacheResponsePlugin]
    ) -> None:
        def _handler(_route_handler: Callable) -> Any:
            pait_core_model: "PaitCoreModel" = getattr(_route_handler, "pait_core_model")
            pait_response: Type[BaseResponseModel] = pait_core_model.response_model_list[0]
            if issubclass(pait_response, HtmlResponseModel) or issubclass(pait_response, TextResponseModel):
                return self.test_helper(self.client, _route_handler).text("get")
            else:
                return self.test_helper(self.client, _route_handler).text("get")

        key: str = "test_cache_other_response_type"
        redis: Redis = Redis(decode_responses=True)
        for route_handler in [text_route, html_route]:
            redis.delete(key)
            with enable_plugin(route_handler, cache_plugin.build(name=key, cache_time=5)):
                assert _handler(route_handler) == _handler(route_handler)

    def cache_response_param_name(
        self, route: Callable, cache_plugin: Type[CacheResponsePlugin], cache_plugin_redis: Any
    ) -> None:
        key: str = "test_cache_response_param_name"
        redis: Redis = Redis(decode_responses=True)

        for _key in redis.scan_iter(match=key + "*"):
            redis.delete(_key)

        with enable_plugin(
            route,
            cache_plugin.build(
                redis=cache_plugin_redis or redis, name=key, enable_cache_name_merge_param=True, cache_time=5
            ),
        ):
            test_helper1: BaseTestHelper = self.test_helper(
                self.client,
                route,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            )
            test_helper2: BaseTestHelper = self.test_helper(
                self.client,
                route,
                body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "woman"},
            )
            assert test_helper1.json() == test_helper1.json()
            assert test_helper2.json() == test_helper2.json()
            assert test_helper1.json() != test_helper2.json()

    @staticmethod
    def grpc_openapi_by_protobuf_file(
        app: Any, grpc_gateway_route: Type[BaseGrpcGatewayRoute], load_app: Callable
    ) -> None:
        import os

        from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
        from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc

        project_path: str = os.getcwd().split("pait/")[0]
        if project_path.endswith("pait"):
            project_path += "/"
        elif not project_path.endswith("pait/"):
            project_path = os.path.join(project_path, "pait/")
        grpc_path: str = project_path + "example/example_grpc/"

        prefix: str = "/api-test"

        grpc_gateway_route(
            app,
            user_pb2_grpc.UserStub,
            social_pb2_grpc.BookSocialStub,
            manager_pb2_grpc.BookManagerStub,
            prefix=prefix + "/",
            title="Grpc-test",
            parse_msg_desc=grpc_path,
            gen_response_model_handle=gen_response_model_handle,
        )
        grpc_test_openapi(load_app(app), url_prefix=prefix)

    @staticmethod
    def grpc_openapi_by_option(app: Any, grpc_gateway_route: Type[BaseGrpcGatewayRoute], load_app: Callable) -> None:
        from example.example_grpc.python_example_proto_code.example_proto_by_option.book import (
            manager_pb2_grpc,
            social_pb2_grpc,
        )
        from example.example_grpc.python_example_proto_code.example_proto_by_option.user import user_pb2_grpc

        prefix: str = "/api-test-by-option"

        grpc_gateway_route(
            app,
            user_pb2_grpc.UserStub,
            social_pb2_grpc.BookSocialStub,
            manager_pb2_grpc.BookManagerStub,
            prefix=prefix + "/",
            title="Grpc-test",
            gen_response_model_handle=gen_response_model_handle,
        )
        grpc_test_openapi(load_app(app), url_prefix=prefix, option_str="_by_option")

        from pait.api_doc.openapi import OpenAPI

        pait_openapi: OpenAPI = OpenAPI(load_app(app))
        assert (
            pait_openapi.dict["paths"]["/api-test-by-option/book/get-book-like"]["post"]["pait_info"]["md5"]
            == pait_openapi.dict["paths"]["/api-test-by-option/book_social_by_option-BookSocial/get_book_like"]["get"][
                "pait_info"
            ]["md5"]
        )
