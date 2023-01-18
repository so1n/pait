import importlib
import sys
from unittest import mock

import pytest
from pytest_mock import MockFixture

from pait.app import any
from pait.app.auto_load_app import app_list, auto_load_app_class
from pait.app.base import BaseAppHelper
from pait.app.base.adapter.request import BaseRequest


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
        pass

        from pait.field import Header

        for i in app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            patch = mocker.patch(f"pait.app.{i}.security.api_key.api_key")
            api_key_func = getattr(importlib.import_module("pait.app.any.security.api_key"), "api_key")
            api_key_func(name="demo", field=Header.i(), verify_api_key_callable=lambda x: True)
            patch.assert_called()


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
