import datetime
import inspect
import traceback
from typing import Any, List

import pytest
from pydantic import BaseModel, Field

from pait import _pydanitc_adapter, field, rule
from pait.app.base import BaseAppHelper
from pait.exceptions import NotFoundValueException
from pait.model import response
from pait.model.core import PaitCoreModel
from pait.param_handle import ParamHandler
from pait.param_handle import util as param_handle_util


class TestParamPlugin:
    def test_depend_return_type(self) -> None:
        def depend_demo(value: str = field.Query.i()) -> int:
            return 0

        def demo(value: str = field.Depends.i(depend_demo)) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "Depends.callable return annotation must:<class 'str'>, not <class 'int'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_error_default_value(self) -> None:
        def demo(value: str = field.Query.i(default=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "default type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_error_default_factory_value(self) -> None:
        def demo(value: str = field.Query.i(default_factory=datetime.datetime.now)) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "default_factory type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_error_example_value(self) -> None:
        def demo(value: str = field.Query.i(example=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo,
                    BaseAppHelper,
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "example type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

        def demo1(value: str = field.Query.i(example=datetime.datetime.now())) -> None:
            pass

        try:
            ParamHandler.pre_check_hook(
                PaitCoreModel(
                    demo1,
                    BaseAppHelper,
                    ParamHandler,
                    response_model_list=[response.JsonResponseModel, response.TextResponseModel],
                ),
                {},
            )
        except Exception:
            assert "example type must <class 'str'>" in traceback.format_exc()
        else:
            raise RuntimeError("Test Fail")

    def test_check_func(self) -> None:
        class Demo:
            def demo(self) -> None:
                pass

        def demo() -> None:
            pass

        ParamHandler._check_func(demo)
        try:
            ParamHandler._check_func(Demo.demo)
        except Exception:
            assert " is not a function" in traceback.format_exc()


class TestRule:
    def test_get_real_request_value_by_raw_return_is_true(self) -> None:
        assert rule.get_real_request_value(
            inspect.Parameter(
                "demo",
                inspect.Parameter.POSITIONAL_ONLY,
                default=field.Query.i(raw_return=True),
                annotation=dict,
            ),
            {"demo": 1, "a": 1},
        ) == {"demo": 1, "a": 1}

    def test_get_real_request_value_by_request_value(self) -> None:
        demo_field: field.Query = field.Query.i()
        demo_field.set_request_key("demo")
        assert (
            rule.get_real_request_value(
                inspect.Parameter(
                    "demo",
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=demo_field,
                    annotation=int,
                ),
                {"demo": 1, "a": 1},
            )
            == 1
        )

    def test_get_real_request_value_by_not_found_value(self) -> None:
        demo_field: field.Query = field.Query.i()
        demo_field.set_request_key("demo")

        with pytest.raises(NotFoundValueException):
            assert rule.get_real_request_value(
                inspect.Parameter(
                    "demo",
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=demo_field,
                    annotation=int,
                ),
                {"a": 1},
            )

    def test_get_real_request_value_by_not_found_value_and_custom_exc(self) -> None:
        demo_field: field.Query = field.Query.i(not_value_exception_func=lambda x: RuntimeError())
        demo_field.set_request_key("demo")

        with pytest.raises(RuntimeError):
            assert rule.get_real_request_value(
                inspect.Parameter(
                    "demo",
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=demo_field,
                    annotation=int,
                ),
                {"a": 1},
            )

    def test_validate_request_value(self) -> None:
        demo_field: field.Query = field.Query.i()
        demo_field.set_request_key("demo")
        pait_model_field = _pydanitc_adapter.PaitModelField(
            value_name="demo", annotation=int, field_info=demo_field, request_param="query"
        )

        assert (
            rule.validate_request_value(
                inspect.Parameter(
                    "demo",
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=demo_field,
                    annotation=int,
                ),
                "1",
                pait_model_field,
            )
            == 1
        )

        class Demo(BaseModel):
            a: int = Field()
            b: str = Field()

        assert rule.validate_request_value(
            inspect.Parameter(
                "demo",
                inspect.Parameter.POSITIONAL_ONLY,
                default=demo_field,
                annotation=Demo,
            ),
            {"a": "1", "b": "1"},
            pait_model_field,
        ) == Demo(a=1, b="1")


class TestUtil:
    def test_get_parameter_list_from_pydantic_basemodel(self) -> None:
        class Demo(BaseModel):
            a: int = field.Query.i()
            b: int = field.Query.i()
            c: int = Field()

        parameter_list = param_handle_util.get_parameter_list_from_pydantic_basemodel(
            Demo, default_field_class=field.Body
        )
        assert len(parameter_list) == 3
        assert isinstance(parameter_list[2].default, field.Body)

    def test_get_parameter_list_from_class(self) -> None:
        value: Any = field.Body.i()

        class Demo1(object):
            pass

        class Demo2(object):
            a: int
            b: str = ""
            c: str = value

        assert [] == param_handle_util.get_parameter_list_from_class(Demo1)
        result: List["inspect.Parameter"] = param_handle_util.get_parameter_list_from_class(Demo2)
        assert len(result) == 1
        assert result[0].name == "c"
        assert result[0].annotation == str
        assert result[0].default == value
