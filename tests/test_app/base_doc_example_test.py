from typing import TYPE_CHECKING, Any, Callable, Type

from redis import Redis  # type: ignore

from pait.app.base import BaseTestHelper

if TYPE_CHECKING:
    pass


class BaseTestDocExample(object):
    def __init__(self, client: Any, test_helper: Type[BaseTestHelper]):
        self.client: Any = client
        self.test_helper: Type[BaseTestHelper] = test_helper

    def hello_world_demo(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
            body_dict={"uid": 123, "username": "appl"},
        ).json(
            method="POST"
        ) == {"uid": 123, "user_name": "appl"}

    def how_to_use_field_demo(self, route: Callable) -> None:
        assert {
            "code": 0,
            "data": {
                "age": 2,
                "cookie": {"abcd": "abcd"},
                "email": "example@xxx.com",
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
            cookie_dict={"abcd": "abcd"},
            form_dict={"a": "1", "b": "2", "c": ["3", "4"]},
            query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
            path_dict={"age": 2},
            strict_inspection_check_json_content=False,
        ).json(
            method="POST"
        )

    def how_to_use_field_with_default_demo(self, with_default_route: Callable, route: Callable) -> None:
        assert "123" == self.test_helper(
            self.client,
            with_default_route,
        ).text(method="GET")
        assert "Can not found demo_value value" == self.test_helper(
            self.client,
            route,
        ).text(method="GET")

        assert "456" == self.test_helper(self.client, with_default_route, query_dict={"demo_value": 456}).text(
            method="GET"
        )
        assert "456" == self.test_helper(self.client, route, query_dict={"demo_value": 456}).text(method="GET")

    def how_to_use_field_with_default_factory_demo(self, route1: Callable, route2: Callable) -> None:
        route1_test_helper = self.test_helper(
            self.client,
            route1,
        )
        route2_test_helper = self.test_helper(
            self.client,
            route2,
        )
        assert route1_test_helper.text(method="GET") != route1_test_helper.text(method="GET")
        assert route2_test_helper.text(method="GET") != route2_test_helper.text(method="GET")

    def how_to_use_field_with_alias_demo(self, route: Callable) -> None:
        assert "123" == self.test_helper(
            self.client,
            route,
            header_dict={"Content-Type": "123"},
        ).text(method="GET")

    def how_to_use_field_with_number_verify_demo(self, route: Callable) -> None:
        assert {"data": [2, 1, 3]} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value1": 2, "demo_value2": 1, "demo_value3": 3},
        ).json(method="GET")
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value1": 11, "demo_value2": 1, "demo_value3": 3},
            ).json(method="GET")["data"][0]
        )
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value1": 2, "demo_value2": 1, "demo_value3": 4},
            ).json(method="GET")["data"][0]
        )
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value1": 2, "demo_value2": 2, "demo_value3": 3},
            ).json(method="GET")["data"][0]
        )

    def how_to_use_field_with_sequence_verify_demo(self, route: Callable) -> None:
        assert {"data": [1]} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value": 1},
        ).json(method="GET")
        assert {"data": [1, 2]} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value": [1, 2]},
        ).json(method="GET")
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value": [1, 2, 3]},
            ).json(method="GET")[
                "data"
            ][0]
        )

    def how_to_use_field_with_str_verify_demo(self, route: Callable) -> None:
        assert {"data": "u66666"} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value": "u66666"},
        ).json(method="GET")
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value": "666666"},
            ).json(method="GET")[
                "data"
            ][0]
        )
        assert (
            "ctx"
            in self.test_helper(
                self.client,
                route,
                query_dict={"demo_value": "1"},
            ).json(method="GET")[
                "data"
            ][0]
        )

    def how_to_use_field_with_raw_return_demo(self, route: Callable) -> None:
        assert {"data": {"a": "1", "b": "2"}, "a": "1"} == self.test_helper(
            self.client, route, body_dict={"a": "1", "b": "2"}
        ).json(method="POST")

    def how_to_use_field_with_custom_not_found_exc_demo(self, route: Callable) -> None:
        assert {"data": {"demo_value1": "1", "demo_value2": "2"}} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value1": "1", "demo_value2": "2"},
        ).json(method="GET")
        assert {"data": "Can not found demo_value1 value"} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value2": "2"},
        ).json(method="GET")
        assert {"data": "not found demo_value2 data"} == self.test_helper(
            self.client,
            route,
            query_dict={"demo_value1": "1"},
        ).json(method="GET")

    def how_to_use_type_with_type_is_pydantic_basemodel(self, get_route: Callable, post_route: Callable) -> None:
        assert {"uid": "u12345", "name": "so1n", "age": 10} == self.test_helper(
            self.client,
            get_route,
            query_dict={"uid": "u12345", "name": "so1n", "age": 10},
        ).json(method="GET")
        assert {"uid": "u12345", "name": "so1n", "age": 10} == self.test_helper(
            self.client,
            post_route,
            body_dict={"uid": "u12345", "name": "so1n", "age": 10},
        ).json(method="POST")

    def how_to_use_type_with_type_is_pait_basemodel(self, get_route: Callable, post_route: Callable) -> None:
        get_dict = self.test_helper(
            self.client,
            get_route,
            query_dict={"uid": "u12345", "name": "so1n", "age": 10},
        ).json(method="GET")
        get_dict.pop("request_id")
        assert {"uid": "u12345", "name": "so1n", "age": 10} == get_dict
        post_dict = self.test_helper(
            self.client,
            post_route,
            body_dict={"uid": "u12345", "name": "so1n", "age": 10},
        ).json(method="POST")
        post_dict.pop("request_id")
        assert {"uid": "u12345", "name": "so1n", "age": 10} == post_dict

    def how_to_use_type_with_type_is_request(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
        ).json(
            method="GET"
        ) == {"url": "/api/demo", "method": "GET"}

    def how_to_use_type_with_type_is_customer(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, query_dict={"timestamp": "1600000000"}).json(method="GET") == {
            "time": "2020-09-13T20:26:40"
        }

    def with_depend(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, header_dict={"token": "u12345"}).json(method="GET") == {
            "user": "so1n"
        }
        assert self.test_helper(self.client, route, header_dict={"token": "u123456"}).json(method="GET") == {
            "data": "Can not found by token:u123456"
        }

    def with_nested_depend(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, header_dict={"token": "u12345"}).json(method="GET") == {
            "user": "so1n"
        }
        assert self.test_helper(self.client, route, header_dict={"token": "u123456"}).json(method="GET") == {
            "data": "Can not found by token:u123456"
        }
        assert self.test_helper(self.client, route, header_dict={"token": "fu12345"}).json(method="GET") == {
            "data": "Illegal Token"
        }

    def with_context_manager_depend(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, query_dict={"uid": 999}).json(method="GET") == {
            "code": 0,
            "msg": 999,
        }
        assert self.test_helper(self.client, route, query_dict={"uid": 999, "is_raise": True}).json(method="GET") == {
            "data": ""
        }

    def with_class_depend(self, route: Callable) -> None:
        assert self.test_helper(
            self.client, route, header_dict={"token": "u12345"}, query_dict={"user_name": "so1n"}
        ).json(method="GET") == {"user": "so1n"}
        assert self.test_helper(self.client, route, header_dict={"token": "u12345"}).json(method="GET") == {
            "data": "Can not found user_name value"
        }
        assert self.test_helper(
            self.client, route, header_dict={"token": "u12345"}, query_dict={"user_name": "faker"}
        ).json(method="GET") == {"data": "The specified user could not be found through the token"}

    def with_pre_depend(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, header_dict={"token": "u12345"}).json(method="GET") == {
            "msg": "success"
        }
        assert self.test_helper(self.client, route, header_dict={"token": "u123456"}).json(method="GET") == {
            "data": "Can not found by token:u123456"
        }

    def with_exception_tip(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
        ).json(
            method="GET"
        ) == {"code": -1, "msg": "error param:demo_value, Can not found demo_value value"}
        assert self.test_helper(self.client, route, query_dict={"demo_value": "a"}).json(method="GET") == {
            "code": -1,
            "msg": "check error param: ['query', 'demo_value']",
        }
        assert self.test_helper(self.client, route, query_dict={"demo_value": 3}).json(method="GET") == {
            "code": 0,
            "msg": "",
            "data": 3,
        }

    def openapi_security_with_api_key(
        self,
        cookie_api_key_route: Callable,
        header_api_key_route: Callable,
        query_api_key_route: Callable,
    ) -> None:
        assert self.test_helper(self.client, cookie_api_key_route, cookie_dict={"token": "token"}).json(
            method="GET"
        ) == {"code": 0, "msg": "", "data": "token"}
        assert self.test_helper(self.client, header_api_key_route, header_dict={"token": "token"}).json(
            method="GET"
        ) == {"code": 0, "msg": "", "data": "token"}
        assert self.test_helper(self.client, query_api_key_route, query_dict={"token": "token"}).json(method="GET") == {
            "code": 0,
            "msg": "",
            "data": "token",
        }
        assert "Not authenticated" in self.test_helper(
            self.client, cookie_api_key_route, cookie_dict={"token": ""}
        ).text(method="GET")
        assert "Not authenticated" in self.test_helper(
            self.client, header_api_key_route, header_dict={"token": ""}
        ).text(method="GET")
        assert "Not authenticated" in self.test_helper(self.client, query_api_key_route, query_dict={"token": ""}).text(
            method="GET"
        )

    def openapi_security_with_http(
        self,
        http_basic_route: Callable,
        http_bearer_route: Callable,
        http_digest_route: Callable,
    ) -> None:
        assert self.test_helper(
            self.client, http_basic_route, header_dict={"Authorization": "Basic c28xbjpzbzFu"}
        ).json(method="GET") == {"code": 0, "data": "so1n", "msg": ""}
        assert self.test_helper(self.client, http_bearer_route, header_dict={"Authorization": "Bearer http"}).json(
            method="GET"
        ) == {"code": 0, "data": "http", "msg": ""}
        assert self.test_helper(self.client, http_digest_route, header_dict={"Authorization": "Digest http"}).json(
            method="GET"
        ) == {"code": 0, "data": "http", "msg": ""}
        assert "Not authenticated" in self.test_helper(
            self.client, http_bearer_route, header_dict={"Authorization": "Bearer x"}
        ).text(method="GET")
        assert "Not authenticated" in self.test_helper(
            self.client, http_digest_route, header_dict={"Authorization": "Digest x"}
        ).text(method="GET")

    def openapi_security_with_oauth2(
        self,
        login_route: Callable,
        user_info_route: Callable,
        user_name_route: Callable,
    ) -> None:
        access_token = self.test_helper(
            self.client,
            login_route,
            form_dict={"grant_type": "password", "scope": "user-info", "username": "so1n", "password": "so1n"},
        ).json(method="POST")["access_token"]
        assert self.test_helper(
            self.client, user_info_route, header_dict={"Authorization": f"Bearer {access_token}"}
        ).json(method="GET") == {
            "code": 0,
            "data": {"age": 23, "name": "so1n", "scopes": ["user-info"], "sex": "M", "uid": "123"},
            "msg": "",
        }
        assert "Not authenticated" in self.test_helper(
            self.client, user_name_route, header_dict={"Authorization": f"Bearer {access_token}"}
        ).text(method="GET")

        access_token = self.test_helper(
            self.client,
            login_route,
            form_dict={"grant_type": "password", "scope": "user-name", "username": "so1n1", "password": "so1n1"},
        ).json(method="POST")["access_token"]
        assert self.test_helper(
            self.client, user_name_route, header_dict={"Authorization": f"Bearer {access_token}"}
        ).json(method="GET") == {"code": 0, "data": "so1n1", "msg": ""}
        assert "Not authenticated" in self.test_helper(
            self.client, user_info_route, header_dict={"Authorization": f"Bearer {access_token}"}
        ).text(method="GET")

    def plugin_with_required_plugin(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, query_dict={"uid": "123"}).json(method="GET") == {
            "uid": "123",
            "user_name": None,
            "email": None,
        }

        assert self.test_helper(self.client, route, query_dict={"uid": "123", "email": "aaa"}).json(method="GET") == {
            "data": "email requires param user_name, which if not none"
        }

    def plugin_with_at_most_one_of_plugin(self, route: Callable) -> None:
        assert self.test_helper(self.client, route, query_dict={"uid": "123"}).json(method="GET") == {
            "uid": "123",
            "user_name": None,
            "email": None,
        }

        assert self.test_helper(self.client, route, query_dict={"uid": "123", "email": "aaa"}).json(method="GET") == {
            "uid": "123",
            "user_name": None,
            "email": "aaa",
        }
        assert self.test_helper(self.client, route, query_dict={"uid": "123", "user_name": "so1n"}).json(
            method="GET"
        ) == {"uid": "123", "user_name": "so1n", "email": None}
        assert self.test_helper(
            self.client, route, query_dict={"uid": "123", "user_name": "so1n", "email": "aaa"}
        ).json(method="GET") == {"data": "requires at most one of param email or user_name"}

    def plugin_with_check_json_response_plugin(self, route: Callable) -> None:
        assert self.test_helper(
            self.client, route, query_dict={"uid": "123", "user_name": "so1n", "age": "18", "display_age": "1"}
        ).json(method="GET") == {
            "code": 0,
            "msg": "",
            "data": {"uid": 123, "user_name": "so1n", "email": "example@xxx.com", "age": 18},
        }
        err_msg = self.test_helper(
            self.client,
            route,
            query_dict={"uid": "123", "user_name": "so1n", "age": "18"},
            enable_assert_response=False,
        ).json(method="GET")["data"]
        assert ("data -> age" in err_msg) or ("data.age" in err_msg)

    def plugin_with_auto_complete_json_response_plugin(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
        ).json(method="GET") == {
            "code": 0,
            "data": {
                "image_list": [{}, {}],
                "music_list": [
                    {"name": "music1", "singer": "singer1", "url": "http://music1.com"},
                    {"name": "", "singer": "", "url": "http://music1.com"},
                ],
                "uid": 100,
            },
            "msg": "",
        }

    def plugin_with_mock_plugin(self, route: Callable) -> None:
        assert self.test_helper(
            self.client,
            route,
        ).json(method="GET") == {
            "code": 0,
            "data": {
                "age": 99,
                "email": "example@so1n.me",
                "multi_user_name": ["mock_name"],
                "uid": 666,
                "user_name": "mock_name",
            },
            "msg": "success",
        }

    def plugin_with_cache_plugin(self, route: Callable) -> None:
        def del_key(key: str) -> None:
            redis: Redis = Redis()
            for _key in redis.scan_iter(match=key + "*"):
                redis.delete(_key)

        # test not exc
        del_key("demo")
        ret1 = self.test_helper(self.client, route, query_dict={"key1": "1", "key2": "1"}).text(method="GET")
        ret2 = self.test_helper(self.client, route, query_dict={"key1": "1", "key2": "1"}).text(method="GET")
        ret3 = self.test_helper(self.client, route, query_dict={"key1": "2", "key2": "1"}).text(method="GET")
        assert ret1 == ret2
        assert ret2 != ret3
        assert ret1 != ret3
