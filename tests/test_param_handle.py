import inspect
from typing import Any

import pytest
from pydantic import BaseModel
from pytest_mock import MockFixture

from pait import field, util
from pait.app.base import BaseAppHelper

pytestmark = pytest.mark.asyncio


class Demo:
    pass


class FakeField(field.BaseField):
    pass


class FakePaitBaseModel(BaseModel):
    a: int = field.Body.i()


class FakeAppHelper(BaseAppHelper):
    def cookie(self) -> int:
        return 1

    def header(self) -> int:
        return 1

    def path(self) -> int:
        return 1

    def query(self) -> int:
        return 1

    def body(self) -> int:
        return 1

    def file(self) -> int:
        return 1

    def form(self) -> int:
        return 1

    def multiform(self) -> int:
        return 1

    def multiquery(self) -> int:
        return 1


class AnyStringWith(str):
    def __eq__(self, other: Any) -> bool:
        return self in other


class StringNotIn(str):
    def __eq__(self, other: Any) -> bool:
        return self not in other


class TestUtil:
    def test_raise_and_tip_param_value_is_empty(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.param_handle.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b",
            inspect.Parameter.POSITIONAL_ONLY,
            annotation=str,
        )
        with pytest.raises(Exception):
            raise util.gen_tip_exc(Demo(), Exception(), parameter)
        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))

    def test_raise_and_tip_param_value_is_pait_field(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.param_handle.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=FakeField.i()
        )
        with pytest.raises(Exception):
            raise util.gen_tip_exc(Demo(), Exception(), parameter)

        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))

    def test_raise_and_tip_param_value_is_not_pait_field(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.param_handle.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=""
        )
        with pytest.raises(Exception):
            raise util.gen_tip_exc(Demo(), Exception(), parameter)
        patch.assert_called_with(StringNotIn("alias"))
        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))

    #
    # def test_get_request_value_from_parameter(self) -> None:
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=FakeField.i()
    #     )
    #     with pytest.raises(exceptions.NotFoundFieldError):
    #         param_handle.get_request_value_from_parameter(parameter, FakeAppHelper(None, (), {}))
    #
    #     parameter = inspect.Parameter("b", inspect.Parameter.POSITIONAL_ONLY, annotation=int, default=field.Body.i())
    #     assert 1 == param_handle.get_request_value_from_parameter(parameter, FakeAppHelper(None, (), {}))
    #
    # def test_set_parameter_value_to_args_list(self, mocker: MockFixture) -> None:
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "self",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=Demo,
    #     )
    #     func_sig_list: list = []
    #     fake_app_helper: FakeAppHelper = FakeAppHelper(None, (), {})
    #     param_handle.set_parameter_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[0] == fake_app_helper.cbv_instance
    #
    #     parameter = inspect.Parameter(
    #         "request",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=type(None),
    #     )
    #     param_handle.set_parameter_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[1] == fake_app_helper.request
    #
    #     parameter = inspect.Parameter(
    #         "a",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=FakePaitBaseModel,
    #     )
    #     param_handle.set_parameter_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[2].a == 1
    #
    #     patch = mocker.patch("pait.param_handle.logging.warning")
    #     parameter = inspect.Parameter(
    #         "a",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=str,
    #     )
    #     param_handle.set_parameter_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     patch.assert_called_with(AnyStringWith("Pait not support args"))
    #
    # async def test_async_set_parameter_value_to_args_list(self, mocker: MockFixture) -> None:
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "self",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=Demo,
    #     )
    #     func_sig_list: list = []
    #     fake_app_helper: FakeAppHelper = FakeAppHelper(None, (), {})
    #     await param_handle.async_set_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[0] == fake_app_helper.cbv_instance
    #
    #     parameter = inspect.Parameter(
    #         "request",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=type(None),
    #     )
    #     await param_handle.async_set_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[1] == fake_app_helper.request
    #
    #     parameter = inspect.Parameter(
    #         "a",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=FakePaitBaseModel,
    #     )
    #     await param_handle.async_set_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     assert func_sig_list[2].a == 1
    #     patch = mocker.patch("pait.param_handle.logging.warning")
    #     parameter = inspect.Parameter(
    #         "a",
    #         inspect.Parameter.POSITIONAL_ONLY,
    #         annotation=str,
    #     )
    #     await param_handle.async_set_value_to_args(parameter, fake_app_helper, func_sig_list)
    #     patch.assert_called_with(AnyStringWith("Pait not support args"))
    #
    # def test_request_value_handle_param_value_is_not_pait_field(self) -> None:
    #     fake_app_helper: FakeAppHelper = FakeAppHelper(None, (), {})
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "a", inspect.Parameter.POSITIONAL_ONLY, annotation=FakePaitBaseModel, default="a"
    #     )
    #     with pytest.raises(exceptions.PaitBaseException) as e:
    #         param_handle.request_value_handle(parameter, 1, None, {}, fake_app_helper)
    #
    #     exec_msg: str = e.value.args[0]
    #     assert exec_msg.startswith(f"must use {field.BaseField.__class__.__name__}")
    #
    # def test_request_value_handle_param_value_not_found_and_not_default_value(self) -> None:
    #     fake_app_helper: FakeAppHelper = FakeAppHelper(None, (), {})
    #
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "a", inspect.Parameter.POSITIONAL_ONLY, annotation=FakePaitBaseModel, default=field.Query.i()
    #     )
    #     _dict: Dict[inspect.Parameter, UndefinedType] = {}
    #     param_handle.request_value_handle(parameter, {"fake": ""}, None, _dict, fake_app_helper)
    #     assert _dict[parameter] == Undefined
    #
    # def test_request_value_handle_param_value_request_value_is_not_mapping(self) -> None:
    #     fake_app_helper: FakeAppHelper = FakeAppHelper(None, (), {})
    #
    #     parameter: inspect.Parameter = inspect.Parameter(
    #         "a", inspect.Parameter.POSITIONAL_ONLY, annotation=FakePaitBaseModel, default=field.Query.i()
    #     )
    #     _dict: dict = {}
    #     param_handle.request_value_handle(parameter, 1, None, _dict, fake_app_helper)
    #     assert _dict[parameter] == 1
