import importlib
import sys
from typing import Any, Callable
from unittest import mock

import pytest
from pytest_mock import MockFixture

from pait.app import any
from pait.app.auto_load_app import app_list, auto_load_app_class
from pait.app.base import BaseAppHelper
from pait.app.base.adapter.request import BaseRequest
from pait.app.base.simple_route import SimpleRoute


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


class TestAddDocRoute(BaseTestApp):
    def test_add_doc_route(self, mocker: MockFixture) -> None:
        for i in app_list:
            patch = mocker.patch(f"pait.app.{i}.add_doc_route")
            any.add_doc_route(importlib.import_module(f"example.{i}_example.main_example").create_app())  # type: ignore
            patch.assert_called()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            any.add_doc_route(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_add_doc_route_class(self) -> None:
        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(any)
            assert any.AddDocRoute == getattr(importlib.import_module(f"pait.app.{i}"), "AddDocRoute")


class TestGrpcRoute(BaseTestApp):
    def test_grpc_route_class(self) -> None:
        from pait.app.any import grpc_route

        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(grpc_route)
            assert grpc_route.GrpcGatewayRoute == getattr(
                importlib.import_module(f"pait.app.{i}.grpc_route"), "GrpcGatewayRoute"
            )


class TestSecurity(BaseTestApp):
    def test_security_api_key(self, mocker: MockFixture) -> None:
        from pait.field import Header

        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(importlib.import_module("pait.app.any.security.api_key"))
            api_key_func = getattr(importlib.import_module("pait.app.any.security.api_key"), "api_key")
            api_key = api_key_func(name="demo", field=Header.i(), verify_api_key_callable=lambda x: True)
            # Since partial_wrapper is used, it can only be judged whether the APIKey is used correctly
            getattr(importlib.import_module(f"pait.app.{i}.security.api_key"), "APIKey") in api_key.__class__.__bases__


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
