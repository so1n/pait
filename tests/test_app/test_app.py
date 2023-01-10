import importlib
import sys
from unittest import mock

import pytest
from pytest_mock import MockFixture

from pait import app
from pait.app.base import BaseAppHelper


class TestApp:
    @staticmethod
    def _clean_app_from_sys_module() -> None:
        for i in app.auto_load_app.app_list:
            sys.modules.pop(i, None)

    def test_load_app(self, mocker: MockFixture) -> None:
        for i in app.auto_load_app.app_list:
            patch = mocker.patch(f"pait.app.{i}.load_app")
            app.load_app(importlib.import_module(f"example.{i}_example.main_example").create_app())  # type: ignore
            patch.assert_called_once()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            app.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_add_doc_route(self, mocker: MockFixture) -> None:
        for i in app.auto_load_app.app_list:
            patch = mocker.patch(f"pait.app.{i}.add_doc_route")
            app.add_doc_route(importlib.import_module(f"example.{i}_example.main_example").create_app())  # type: ignore
            patch.assert_called()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            app.add_doc_route(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_pait_class(self) -> None:
        for i in app.auto_load_app.app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(app)
            assert app.Pait == getattr(importlib.import_module(f"pait.app.{i}"), "Pait")

    def test_add_doc_route_class(self) -> None:
        for i in app.auto_load_app.app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(app)
            assert app.AddDocRoute == getattr(importlib.import_module(f"pait.app.{i}"), "AddDocRoute")

    def test_pait(self, mocker: MockFixture) -> None:
        for i in app.auto_load_app.app_list:
            self._clean_app_from_sys_module()
            # import web app
            importlib.import_module(i)
            # reload pait.app
            importlib.reload(app)
            patch = mocker.patch(f"pait.app.{i}.pait")
            app.pait()
            patch.assert_called_once()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            app.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_auto_load_app_class_error(self) -> None:
        self._clean_app_from_sys_module()
        with mock.patch.dict("sys.modules", sys.modules):
            with pytest.raises(RuntimeError) as e:
                app.auto_load_app_class()

        exec_msg: str = e.value.args[0]
        assert exec_msg == "Pait can't auto load app class"

        for i in app.auto_load_app.app_list:
            importlib.import_module(i)
        with mock.patch.dict("sys.modules", sys.modules):
            with pytest.raises(RuntimeError) as e:
                app.auto_load_app_class()

        exec_msg = e.value.args[0]
        assert exec_msg.startswith("Pait unable to make a choice")

    def test_base_app_helper__init__(self, mocker: MockFixture) -> None:
        class Demo:
            pass

        demo = Demo()

        class CustomerAppHelper(BaseAppHelper[None, None]):  # type: ignore
            CbvType = Demo  # type: ignore

        # route func param: self, request, other param
        customer_app_helper: CustomerAppHelper = CustomerAppHelper([demo, None, 1], {"a": 1, "b": 2, "c": 3})
        assert customer_app_helper.request is None
        assert customer_app_helper.cbv_instance == demo
        assert customer_app_helper.request_args == [demo]
        assert customer_app_helper.request_kwargs == {"a": 1, "b": 2, "c": 3}

        # route func param: request
        customer_app_helper = CustomerAppHelper([None], {"a": 1, "b": 2, "c": 3})
        assert customer_app_helper.request is None
        assert customer_app_helper.cbv_instance is None
        assert customer_app_helper.request_args == []
        assert customer_app_helper.request_kwargs == {"a": 1, "b": 2, "c": 3}

        patch = mocker.patch("pait.data.logging.warning")
        # route func param: other param, self, request
        BaseAppHelper([1, demo, None], {"a": 1, "b": 2, "c": 3})
        patch.assert_called_once()

    def test_base_app_helper_check_type(self) -> None:
        class FakeAppHelper(BaseAppHelper):
            RequestType = str
            FormType = int
            FileType = float
            HeaderType = type(None)

        fake_app_helper: FakeAppHelper = FakeAppHelper([], {})
        assert fake_app_helper.check_request_type(type(""))
        assert fake_app_helper.check_form_type(type(0))
        assert fake_app_helper.check_file_type(type(0.0))
        assert fake_app_helper.check_header_type(type(None))
