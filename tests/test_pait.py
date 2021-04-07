import importlib
import inspect
import pytest
import sys
from unittest import mock
from typing import Type

from pytest_mock import MockFixture
from pydantic import BaseModel
from pait import app, core, field, g, util
from example import param_verify


class TestUtil:
    def test_create_pydantic_model(self) -> None:
        pydantic_model_class: Type[BaseModel] = util.create_pydantic_model({"a": (int, ...), "b": (str, ...)})
        pydantic_model = pydantic_model_class(a=1, b="a")
        assert pydantic_model.dict() == {"a": 1, "b": "a"}

    def test_func_sig(self) -> None:
        def demo(a: int, b: str) -> int: pass

        func_sig: util.FuncSig = util.get_func_sig(demo)
        assert func_sig.func == demo
        assert func_sig.sig == inspect.signature(demo)
        sig: inspect.Signature = inspect.signature(demo)
        assert func_sig.param_list == [
            sig.parameters[key]
            for key in sig.parameters
            if sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"
        ]

    def test_get_parameter_list_from_class(self) -> None:
        class Demo1(object):
            pass

        class Demo2(object):
            a: int
            b: str = ""

        assert [] == util.get_parameter_list_from_class(Demo1)
        assert [
           inspect.Parameter(
               "a",
               inspect.Parameter.POSITIONAL_ONLY,
               default=util.Undefined,
               annotation=int,
           ),
           inspect.Parameter(
               "b",
               inspect.Parameter.POSITIONAL_ONLY,
               default="",
               annotation=str,
           )
        ] == util.get_parameter_list_from_class(Demo2)


class TestPaitCore:
    def test_pait_core(self) -> None:
        with pytest.raises(TypeError) as e:
            @core.pait("a")
            def demo() -> None: pass

        exec_msg: str = e.value.args[0]
        assert exec_msg.endswith("must be class")

        with pytest.raises(RuntimeError) as e:

            class Demo:
                pass

            @core.pait(Demo)
            def demo() -> None: pass

        exec_msg = e.value.args[0]
        assert exec_msg == "Please check pait app helper or func"

    def test_pait_id_not_in_data(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.data.logging.warning")
        g.pait_data.add_route_info("fake_id", "/", {"get"}, "fake")
        patch.assert_called_once()

    def test_pait_id_in_data(self, mocker: MockFixture) -> None:
        pait_id: str = list(g.pait_data.pait_id_dict.keys())[0]
        g.pait_data.add_route_info(pait_id, "/", {"get"}, "fake")
        assert g.pait_data.pait_id_dict[pait_id].path == "/"
        assert g.pait_data.pait_id_dict[pait_id].method_list == ["get"]
        assert g.pait_data.pait_id_dict[pait_id].operation_id == "fake"
        assert g.pait_data


class TestField:
    def test_call_base_field(self) -> None:
        with pytest.raises(RuntimeError):
            field.BaseField()

    def test_error_inherit_base_field(self) -> None:
        class Demo(field.Body):
            pass

        with pytest.raises(RuntimeError):
            Demo()


class TestApp:

    @staticmethod
    def _clean_app_from_sys_module() -> None:
        for i in app.auto_load_app.app_list:
            sys.modules.pop(i, None)

    def test_load_app(self, mocker: MockFixture) -> None:
        for i in app.auto_load_app.app_list:
            patch = mocker.patch(f"pait.app.{i}.load_app")
            app.load_app(getattr(param_verify, f"{i}_example").app)
            patch.assert_called_once()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            app.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_pait(self, mocker: MockFixture) -> None:
        for i in app.auto_load_app.app_list:
            self._clean_app_from_sys_module()
            importlib.import_module(i)
            patch = mocker.patch(f"pait.app.{i}.pait")
            app.pait()
            patch.assert_called_once()

        class Demo:
            pass

        with pytest.raises(NotImplementedError) as e:
            app.load_app(Demo)

        exec_msg: str = e.value.args[0]
        assert exec_msg.startswith("Pait not support")

    def test_auto_load_app_class_errpr(self) -> None:
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
