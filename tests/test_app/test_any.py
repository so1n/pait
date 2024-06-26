import importlib
import sys
from typing import Any, Callable
from unittest import mock

import pytest
from pytest_mock import MockFixture

from pait.app import any
from pait.app.any.util import base_call_func, import_func_from_app, sniffing, sniffing_dict
from pait.app.auto_load_app import app_list, auto_load_app_class
from pait.app.base import BaseAppHelper
from pait.app.base.adapter.request import BaseRequest
from pait.app.base.simple_route import SimpleRoute
from pait.param_handle.base import BaseParamHandler


class BaseTestApp:
    @staticmethod
    def _clean_app_from_sys_module() -> None:
        for i in app_list:
            sys.modules.pop(i, None)


class TestLoadApp(BaseTestApp):
    def test_load_app(self, mocker: MockFixture) -> None:
        for i in app_list:
            patch = mocker.patch(f"pait.app.{i}.load_app")
            any.load_app(importlib.import_module(f"example.{i}_example.main_example").create_app())  # type: ignore
            patch.assert_called()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            any.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")


class TestAutoLoadApp(BaseTestApp):
    def test_auto_load_app_class_error(self) -> None:
        self._clean_app_from_sys_module()
        with mock.patch.dict("sys.modules", sys.modules):
            with pytest.raises(RuntimeError) as e:
                auto_load_app_class()

        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait can't auto load app class"

        for i in app_list:
            importlib.import_module(i)
        with mock.patch.dict("sys.modules", sys.modules):
            with pytest.raises(RuntimeError) as e:
                auto_load_app_class()

        exec_msg = e.value.args[0]
        assert exec_msg.startswith("Pait unable to make a choice")


class TestHttpException(BaseTestApp):
    def test_http_exception(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any"))
            any.http_exception(status_code=200, message="foo")

            assert any.http_exception == getattr(importlib.import_module(f"pait.app.{i}"), "http_exception")


class TestSecurity(BaseTestApp):
    def test_security_api_key(self) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any.security.api_key"))
            APIKey = getattr(importlib.import_module("pait.app.any.security.api_key"), "APIKey")
            # Since partial_wrapper is used, it can only be judged whether the APIKey is used correctly
            getattr(importlib.import_module(f"pait.app.{i}.security.api_key"), "APIKey") in APIKey.__bases__

    def test_security_oauth2_password_bearer(self) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any.security.oauth2"))
            OAuth2PasswordBearer = getattr(
                importlib.import_module("pait.app.any.security.oauth2"), "OAuth2PasswordBearer"
            )
            # Since partial_wrapper is used, it can only be judged whether the OAuth2PasswordBearer is used correctly
            getattr(
                importlib.import_module(f"pait.app.{i}.security.oauth2"), "OAuth2PasswordBearer"
            ) in OAuth2PasswordBearer.__bases__

    def test_security_http(self) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any.security.http"))
            for item in ["HTTPBasic", "HTTPDigest", "HTTPBearer"]:
                class_ = getattr(importlib.import_module("pait.app.any.security.http"), item)
                # Since partial_wrapper is used, it can only be judged whether the class_ is used correctly
                getattr(importlib.import_module(f"pait.app.{i}.security.http"), item) in class_.__bases__


class TestPait(BaseTestApp):
    def test_pait_class(self) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any"))
            assert any.Pait == getattr(importlib.import_module(f"pait.app.{i}"), "Pait")

    def test_pait(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(any)
            patch = mocker.patch(f"pait.app.{i}.pait")
            any.pait()
            patch.assert_called_once()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            any.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")


def demo() -> Any:
    return None


empty_simple_route: SimpleRoute = SimpleRoute(url="/", methods=["get"], route=demo)


class TestAttribute(BaseTestApp):
    def test_set_app_attribute(self, mocker: MockFixture) -> None:
        for i in app_list:
            patch = mocker.patch(f"pait.app.{i}.set_app_attribute")
            any.set_app_attribute(
                importlib.import_module(f"example.{i}_example.main_example").create_app(), "a", 1  # type: ignore
            )
            patch.assert_called()

    def test_get_app_attribute(self, mocker: MockFixture) -> None:
        for i in app_list:
            # test not found
            with pytest.raises(KeyError):
                any.get_app_attribute(
                    importlib.import_module(f"example.{i}_example.main_example").create_app(),  # type: ignore
                    "a",
                )
            # test default value
            assert "aaa" == any.get_app_attribute(
                importlib.import_module(f"example.{i}_example.main_example").create_app(), "a", "aaa"  # type: ignore
            )

            patch = mocker.patch(f"pait.app.{i}.set_app_attribute")
            any.get_app_attribute(
                importlib.import_module(f"example.{i}_example.main_example").create_app(), "a", "demo"  # type: ignore
            )
            patch.assert_called()


class TestAddSimpleRoute(BaseTestApp):
    def test_add_simple_route(self, mocker: MockFixture) -> None:
        for i in app_list:
            patch = mocker.patch(f"pait.app.{i}.add_simple_route")
            any.add_simple_route(
                importlib.import_module(f"example.{i}_example.main_example").create_app(),  # type: ignore
                empty_simple_route,
            )
            patch.assert_called()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            any.add_simple_route(Demo, empty_simple_route)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_add_multi_simple_route(self, mocker: MockFixture) -> None:
        for i in app_list:
            patch = mocker.patch(f"pait.app.{i}.add_multi_simple_route")
            any.add_multi_simple_route(
                importlib.import_module(f"example.{i}_example.main_example").create_app(),  # type: ignore
                empty_simple_route,
            )
            patch.assert_called()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            any.add_multi_simple_route(Demo, empty_simple_route)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")


class TestAppHelper(BaseTestApp):
    def test_base_app_helper__init__(self, mocker: MockFixture) -> None:
        class Demo:
            pass

        demo = Demo()

        class PaitRequestDemo(BaseRequest):
            RequestType = str

        class CustomerAppHelper(BaseAppHelper[None, None]):  # type: ignore
            CbvType = Demo  # type: ignore
            request_class = PaitRequestDemo

        # route func param: self, request, other param
        arg_list = [demo, "", 1]
        customer_app_helper: CustomerAppHelper = CustomerAppHelper(arg_list, {"a": 1, "b": 2, "c": 3})
        assert isinstance(customer_app_helper.request.request, str)
        assert customer_app_helper.cbv_instance == demo
        assert customer_app_helper.request.args == arg_list
        assert customer_app_helper.request.request_kwargs == {"a": 1, "b": 2, "c": 3}

        # route func param: request
        arg_list = [""]
        customer_app_helper = CustomerAppHelper(arg_list, {"a": 1, "b": 2, "c": 3})
        assert isinstance(customer_app_helper.request.request, str)
        assert customer_app_helper.cbv_instance is None
        assert customer_app_helper.request.args == arg_list
        assert customer_app_helper.request.request_kwargs == {"a": 1, "b": 2, "c": 3}

        # patch = mocker.patch("pait.data.logging.warning")
        # # route func param: other param, self, request
        # BaseAppHelper([1, demo, None], {"a": 1, "b": 2, "c": 3})
        # patch.assert_called_once()

    def test_base_app_helper_check_type(self) -> None:
        from pait.app.base.adapter.request import BaseRequest

        class FakeRequest(BaseRequest):
            RequestType = str
            FormType = int
            FileType = float
            HeaderType = type(None)

        class FakeAppHelper(BaseAppHelper):
            request_class = FakeRequest

        fake_app_helper: FakeAppHelper = FakeAppHelper([""], {})
        assert fake_app_helper.request.check_request_type(type(""))
        assert fake_app_helper.request.check_form_type(type(0))
        assert fake_app_helper.request.check_file_type(type(0.0))
        assert fake_app_helper.request.check_header_type(type(None))


class TestPlugin(BaseTestApp):
    class FakePluginCoreModel:
        func: Callable = lambda: None
        param_handler_plugin = BaseParamHandler

    def test_at_most_one_of(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            from pait.app.any import plugin

            importlib.reload(plugin)
            patch = mocker.patch(f"pait.app.{i}.plugin.AtMostOneOfPlugin.__post_init__")
            plugin_class = getattr(importlib.import_module("pait.app.any.plugin"), "AtMostOneOfPlugin")
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_auto_complete_json_resp(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any.plugin import auto_complete_json_resp

            importlib.reload(auto_complete_json_resp)
            patch = mocker.patch(
                f"pait.app.{i}.plugin.auto_complete_json_resp.AutoCompleteJsonRespPlugin.__post_init__"
            )
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin.auto_complete_json_resp"), "AutoCompleteJsonRespPlugin"
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_mock_plugin(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any.plugin import mock_response

            importlib.reload(mock_response)
            patch = mocker.patch(f"pait.app.{i}.plugin.mock_response.MockPlugin.__post_init__")
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin.mock_response"),
                "MockPlugin",
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_cache_response(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any.plugin import cache_response

            importlib.reload(cache_response)
            patch = mocker.patch(f"pait.app.{i}.plugin.cache_response.CacheResponsePlugin.__post_init__")
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin.cache_response"),
                "CacheResponsePlugin",
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_check_json_resp(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any.plugin import check_json_resp

            importlib.reload(check_json_resp)
            patch = mocker.patch(f"pait.app.{i}.plugin.check_json_resp.CheckJsonRespPlugin.__post_init__")
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin.check_json_resp"),
                "CheckJsonRespPlugin",
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_required(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any import plugin

            importlib.reload(plugin)
            patch = mocker.patch(f"pait.app.{i}.plugin.RequiredPlugin.__post_init__")
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin"),
                "RequiredPlugin",
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()

    def test_unified_response(self, mocker: MockFixture) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            from pait.app.any.plugin import unified_response

            importlib.reload(unified_response)
            patch = mocker.patch(f"pait.app.{i}.plugin.unified_response.UnifiedResponsePlugin.__post_init__")
            plugin_class = getattr(
                importlib.import_module("pait.app.any.plugin.unified_response"),
                "UnifiedResponsePlugin",
            )
            plugin_class(lambda *args, **kwargs: None, self.FakePluginCoreModel())
            patch.assert_called()


class TestUtil(BaseTestApp):
    def test_sniffing(self) -> None:
        from flask import Flask

        assert sniffing(Flask("demo")) == "flask"

        from sanic import Sanic

        assert sniffing(Sanic("demo")) == "sanic"

        from starlette.applications import Starlette

        assert sniffing(Starlette()) == "starlette"

        from tornado.web import Application

        assert sniffing(Application()) == "tornado"

    def test_sniffing_not_found(self) -> None:
        class FakeAppDemo(object):
            pass

        with pytest.raises(NotImplementedError):
            sniffing(FakeAppDemo)

    def test_sniffing_with_sniffing_dict(self) -> None:
        class FakeAppDemo(object):
            pass

        sniffing_dict[FakeAppDemo] = lambda x: "demo"
        try:
            assert sniffing(FakeAppDemo()) == "demo"
        finally:
            sniffing_dict.pop(FakeAppDemo)

    def test_import_func_from_app(self) -> None:
        from flask import Flask

        from pait.app.flask import pait
        from pait.app.flask.security.api_key import APIKey

        assert import_func_from_app("pait", app=Flask("demo")) == pait
        assert import_func_from_app("APIKey", app=Flask("demo"), module_name="security.api_key") == APIKey

    def test_auto_import_func_from_app(self) -> None:
        self._clean_app_from_sys_module()
        with mock.patch.dict("sys.modules", sys.modules):
            import flask  # isort: skip
            from pait.app.flask import pait

            assert import_func_from_app("pait") == pait

        self._clean_app_from_sys_module()
        with mock.patch.dict("sys.modules", sys.modules):
            import sanic  # isort: skip
            from pait.app.sanic import pait  # type: ignore[assignment]

            assert import_func_from_app("pait") == pait

    def test_base_call_func(self) -> None:
        from flask import Flask

        my_pait = base_call_func("pait", app=Flask("demo"), author=("so1n",))
        my_pait.author = ("so1n",)
