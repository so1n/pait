import hashlib
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

import pytest
from pytest_mock import MockFixture
from redis import Redis  # type: ignore

from pait.app.base import BaseTestHelper, CheckResponseException
from pait.model.core import get_core_model
from pait.model.response import BaseResponseModel, FileResponseModel, HtmlResponseModel, TextResponseModel
from pait.plugin.cache_response import CacheResponsePlugin
from pait.plugin.mock_response import MockPluginProtocol
from tests.conftest import enable_plugin, enable_resp_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class BaseTest(object):
    def __init__(self, client: Any, test_helper: Type[BaseTestHelper]):
        self.client: Any = client
        self.test_helper: Type[BaseTestHelper] = test_helper

    def raise_tip_route(
        self, route: Callable, is_raise: bool = True, mocker: Optional[MockFixture] = None, debug_logger: Any = None
    ) -> None:
        if mocker:
            debug_logger = mocker.patch("pait.util._gen_tip.logging.debug")
        if not debug_logger:
            raise RuntimeError("mocker or debug_logger must be not None")
        msg: str = self.test_helper(
            self.client, route, header_dict={"Content-Type": "test"}, body_dict={"temp": None}
        ).json()["msg"]
        assert msg.startswith("error param:content__type, Can not found content__type value")
        if is_raise:
            assert "<-- error" in debug_logger.call_args[0][0]
        else:
            debug_logger.assert_not_called()

    def raise_not_tip_route(self, route: Callable) -> None:
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
        assert {
            "code": 0,
            "msg": "",
            "data": {
                "age": 2,
                "user_agent": "customer_agent",
                "user_info": {
                    "uid": 100,
                    "user_name": "so1n",
                },
            },
        } == self.test_helper(
            self.client,
            route,
            header_dict={"user-agent": "customer_agent"},
            body_dict={"age": 2},
            query_dict={"uid": 100, "user_name": "so1n"},
            strict_inspection_check_json_content=False,
        ).json()

    def pre_depend_route(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, header_dict={"token": "demo"}).json()["code"] == 0
        assert self.test_helper(self.client, route).json()["code"] != 0

    def same_alias_name(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
            query_dict={"token": "query"},
            header_dict={"token": "header"},
            strict_inspection_check_json_content=False,
        ).json() == {"code": 0, "msg": "", "data": {"query_token": "query", "header_token": "header"}}
        assert self.test_helper(
            self.client,
            route,
            query_dict={"token": "query1"},
            header_dict={"token": "header1"},
            strict_inspection_check_json_content=False,
        ).json() == {"code": 0, "msg": "", "data": {"query_token": "query1", "header_token": "header1"}}

    def field_default_factory_route(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
            body_dict={"demo_value": 0},
            strict_inspection_check_json_content=False,
        ).json() == {"code": 0, "msg": "", "data": {"demo_value": 0, "data_list": [], "data_dict": {}}}

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
        with NamedTemporaryFile(delete=True) as f1:
            f1.write(file_content.encode())
            f1.seek(0)
            assert (
                "miss param: ['path', 'age']"
                == self.test_helper(
                    self.client,
                    route,
                    file_dict={"upload_file": f1},
                    cookie_dict={"abcd": "abcd"},
                    form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
                    query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                    path_dict={"age": 101},
                    strict_inspection_check_json_content=False,
                ).json()["msg"]
            )

    def param_at_most_one_of_route(self, route: Callable) -> None:
        test_helper: BaseTestHelper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert "requires at most one of param user_name or alias_user_name" in test_helper.json()["msg"]
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "other_user_name": "appl", "alias_user_name": "appe"},
            strict_inspection_check_json_content=False,
        )
        assert (
            "requires at most one of param alias_user_name or other_user_name" in test_helper.json()["msg"]
            or "requires at most one of param other_user_name or alias_user_name" in test_helper.json()["msg"]
        )

        for column in ["user_name", "alias_user_name", "other_user_name"]:
            test_helper = self.test_helper(
                self.client,
                route,
                query_dict={"uid": 123, column: "appl"},
                strict_inspection_check_json_content=False,
            )
        assert test_helper.json()["code"] == 0

    def param_required_route(self, route: Callable) -> None:
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "email": "example@example.com"},
            strict_inspection_check_json_content=False,
        )
        assert "email requires param birthday, which if not none" in test_helper.json()["msg"]
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "email": "example@example.com", "birthday": "2000-01-01"},
            strict_inspection_check_json_content=False,
        )
        assert test_helper.json()["code"] == 0
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl"},
            strict_inspection_check_json_content=False,
        )
        assert "user_name requires param sex, which if not none" in test_helper.json()["msg"]
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man"},
            strict_inspection_check_json_content=False,
        )
        assert test_helper.json()["code"] == 0

    def check_response(self, route: Callable) -> None:
        test_helper: BaseTestHelper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(CheckResponseException):
            test_helper.json()
        test_helper = self.test_helper(
            self.client,
            route,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.json()

    def mock_route(self, route: Callable) -> None:
        resp_model = get_core_model(route).response_model_list[0]
        assert (
            self.test_helper(
                self.client,
                route,
                path_dict={"age": 3},
                query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            ).json()
            == resp_model.get_example_value()
        )
        # test mock file response fail and close contextmanager
        with enable_resp_model(route, FileResponseModel):
            with enable_plugin(route, MockPluginProtocol.build(), is_replace=True):
                assert (
                    self.test_helper(
                        self.client,
                        route,
                        path_dict={"age": 3},
                        query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
                        enable_assert_response=False,
                    ).json()["msg"]
                    == "Not Implemented"
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
            error_logger = mocker.patch("example.common.depend.logging.error")
            info_logger = mocker.patch("example.common.depend.logging.info")
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
            error_logger = mocker.patch("example.common.depend.logging.error")
            info_logger = mocker.patch("example.common.depend.logging.info")
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

    def base_sync_depend_route(self, route: Callable, request_dict: dict) -> None:
        test_helper = self.test_helper(self.client, route, strict_inspection_check_json_content=False, **request_dict)
        assert test_helper.json() == {"code": 0, "msg": "", "data": {"uid": 10086, "name": "so1n"}}

    def api_key_route(self, route: Callable, request_dict: dict) -> None:
        test_helper = self.test_helper(self.client, route, strict_inspection_check_json_content=False)
        resp = test_helper.get()
        assert 403 == test_helper._get_status_code(resp)
        assert "Not authenticated" in test_helper._get_text(resp)

        assert (
            self.test_helper(self.client, route, strict_inspection_check_json_content=False, **request_dict).json()[
                "data"
            ]
            == "my-token"
        )

    def oauth2_password_route(
        self, *, login_route: Callable, user_name_route: Callable, user_info_route: Callable
    ) -> None:
        # test_helper = self.test_helper(self.client, user_name_route, strict_inspection_check_json_content=False)
        # assert 401 == test_helper._get_status_code(test_helper.get())
        #
        # test_helper = self.test_helper(self.client, user_info_route, strict_inspection_check_json_content=False)
        # assert 401 == test_helper._get_status_code(test_helper.get())
        #
        test_helper = self.test_helper(
            self.client,
            login_route,
            form_dict={"username": "so1n", "password": "1"},
            strict_inspection_check_json_content=False,
        )
        # assert 400 == test_helper._get_status_code(test_helper.post())

        for test_dict in [
            # not scopes
            {"scopes": "", "status_code": 401, "route": user_name_route, "data": None},
            {"scopes": "", "status_code": 401, "route": user_info_route, "data": None},
            # error scopes
            {"scopes": "user-info", "status_code": 401, "route": user_name_route, "data": None},
            {"scopes": "user-name", "status_code": 401, "route": user_info_route, "data": None},
            # right scopes
            {"scopes": "user-name", "status_code": 200, "route": user_name_route, "data": "so1n"},
            {
                "scopes": "user-info",
                "status_code": 200,
                "route": user_info_route,
                "data": {"age": 23, "name": "so1n", "scopes": ["user-info"], "sex": "M", "uid": "123"},
            },
            {"scopes": "user-info user-name", "status_code": 200, "route": user_name_route, "data": "so1n"},
            {
                "scopes": "user-info user-name",
                "status_code": 200,
                "route": user_info_route,
                "data": {"age": 23, "name": "so1n", "scopes": ["user-info", "user-name"], "sex": "M", "uid": "123"},
            },
        ]:
            from example.common.security import temp_token_dict

            temp_token_dict.clear()

            resp_dict = self.test_helper(
                self.client,
                login_route,
                form_dict={"username": "so1n", "password": "so1n", "scope": test_dict["scopes"]},
                strict_inspection_check_json_content=False,
            ).json()
            assert resp_dict["token_type"] == "bearer"

            resp = self.test_helper(
                self.client,
                test_dict["route"],  # type: ignore
                header_dict={"Authorization": f"Bearer {resp_dict['access_token']}"},
                strict_inspection_check_json_content=False,
            ).get()
            assert test_dict["status_code"] == test_helper._get_status_code(resp)
            resp_data = test_dict["data"]
            if resp_data:
                assert resp_data == test_helper._get_json(resp)["data"]

    def get_user_name_by_http_bearer(self, route: Callable) -> None:
        for header_dict, status_code in [
            ({}, 403),  # not data
            ({"Authorization": "http-token"}, 403),  # not schema
            ({"Authorization": "Bearer token"}, 403),  # fail token
            ({"Authorization": "Beare http-token"}, 403),  # fail schema
            ({"Authorization": "Bearer http-token"}, 200),
        ]:
            test_helper = self.test_helper(
                self.client, route, header_dict=header_dict, strict_inspection_check_json_content=False  # type: ignore
            )
            assert test_helper._get_status_code(test_helper.get()) == status_code

    def get_user_name_by_http_digest(self, route: Callable) -> None:
        for header_dict, status_code in [
            ({}, 403),  # not data
            ({"Authorization": "http-token"}, 403),  # not schema
            ({"Authorization": "Digest token"}, 403),  # fail token
            ({"Authorization": "Diges http-token"}, 403),  # fail schema
            ({"Authorization": "Digest http-token"}, 200),
        ]:
            test_helper = self.test_helper(
                self.client, route, header_dict=header_dict, strict_inspection_check_json_content=False  # type: ignore
            )
            assert test_helper._get_status_code(test_helper.get()) == status_code

    def get_user_name_by_http_basic_credentials(self, route: Callable) -> None:
        from base64 import b64encode

        for header_dict, status_code in [
            ({}, 401),  # not data
            ({"Authorization": b64encode(b"http-token").decode()}, 401),  # not scheme
            ({"Authorization": "Basic so1n:so1n"}, 401),  # can not decode
            ({"Authorization": f"Basic {b64encode(b'so1n:').decode()}"}, 401),  # not pw
            ({"Authorization": f"Basic {b64encode(b'so1n:so1n').decode()}"}, 200),
        ]:
            test_helper = self.test_helper(
                self.client, route, header_dict=header_dict, strict_inspection_check_json_content=False  # type: ignore
            )
            assert test_helper._get_status_code(test_helper.get()) == status_code

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
        result3: str = self.test_helper(self.client, cache_response1, query_dict={"key1": 1, "key2": 2}).text()
        result4: str = self.test_helper(self.client, cache_response1, query_dict={"key1": 1, "key2": 3}).text()
        assert result1 == result2
        assert result3 == result4
        assert result1 != result3
        assert result2 != result4
        del_key(key)
        assert result1 != self.test_helper(self.client, cache_response).text()
        assert result3 != self.test_helper(self.client, cache_response1, query_dict={"key1": 1, "key2": 2}).text()

        # test query key1 diff
        assert (
            self.test_helper(self.client, cache_response1, query_dict={"key1": 1, "key2": 2}).text()
            != self.test_helper(self.client, cache_response1, query_dict={"key1": 2, "key2": 2}).text()
        )

        # test not include exc
        del_key(key)
        if not app:
            assert self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).json()["code"] == -1
            # with pytest.raises(CheckResponseException) as e:
            #     self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).text()
            #
            # assert e.value.status_code == 500
        elif app == "sanic":
            with pytest.raises(CheckResponseException) as e:
                self.test_helper(self.client, cache_response, query_dict={"raise_exc": 1}).text()

            assert e.value.status_code == 500
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

    def unified_html_response(self, route: Callable) -> None:
        assert self.test_helper(self.client, route).text() == "<html>Demo</html>"

    def unified_text_response(self, route: Callable) -> None:
        assert self.test_helper(self.client, route).text() == "Demo"

    def unified_json_response(self, route: Callable) -> None:
        assert self.test_helper(self.client, route).json() == {"data": "Demo"}

    def any_type(self, route: Callable) -> None:
        first_call_result = self.test_helper(self.client, route).json()["data"]
        second_call_result = self.test_helper(self.client, route).json()["data"]
        assert isinstance(first_call_result, int)
        assert isinstance(second_call_result, int)
        assert first_call_result == second_call_result

    def tag(self, route: Callable) -> None:
        result = self.test_helper(self.client, route).json()["data"]
        assert result["include"] == "include-value"
        assert result["exclude"] == "exclude-value"

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

    def file_route(self, route: Callable, ignore_path: bool = False) -> None:
        file_content: str = "Hello Word!"
        with NamedTemporaryFile(delete=True) as f:
            f.write(file_content.encode())
            f.seek(0)
            assert {
                "filename": f.name.split("/")[-1] if ignore_path else f.name,
                "length": len(file_content),
                # "filename":  f.name, "length": len(file_content)
            } == self.test_helper(
                self.client,
                route,
                file_dict={"stream": f},
            ).json()

    def api_route_health(self, route: Callable) -> None:
        assert self.test_helper(self.client, route).json() == {"code": 0, "msg": "ok", "data": {}}

    def api_route_login(self, route: Callable) -> None:
        assert (
            self.test_helper(self.client, route, body_dict={"uid": "10086", "password": "123"}).json()["data"]["token"]
            == hashlib.sha256(("10086" + "123").encode("utf-8")).hexdigest()
        )

    def api_route_get_user_info(self, route: Callable) -> None:
        assert self.test_helper(
            self.client, route, query_dict={"uid": 100, "user_name": "so1n"}, strict_inspection_check_json_content=False
        ).json() == {"code": 0, "msg": "ok", "data": {"uid": 100, "user_name": "so1n"}}

    def api_route_cbv(self, cbv_route: Type) -> None:
        cbv_get_route = getattr(cbv_route, "get")
        cbv_post_route = getattr(cbv_route, "post")
        assert self.test_helper(
            self.client,
            cbv_get_route,
            header_dict={"Content-Type": "application/json"},
            query_dict={"uid": 100, "user_name": "so1n"},
            strict_inspection_check_json_content=False,
        ).json() == {
            "code": 0,
            "msg": "ok",
            "data": {"uid": 100, "user_name": "so1n"},
            "content_type": "application/json",
        }
        assert (
            self.test_helper(
                self.client,
                cbv_post_route,
                body_dict={"uid": "10086", "password": "123"},
                header_dict={"Content-Type": "application/json"},
            ).json()["data"]["token"]
            == hashlib.sha256(("10086" + "123").encode("utf-8")).hexdigest()
        )
