import datetime
import enum
import inspect
import typing
from typing import Any, Dict, Generator, List, Optional, Union

import pytest
import typing_extensions
from pydantic import BaseModel, Field, conint, constr
from pytest_mock import MockFixture

from pait import _pydanitc_adapter, field, util
from pait.exceptions import TipException

pytestmark = pytest.mark.asyncio


class TestFuncSig:
    def test_get_pait_handler(self) -> None:
        class WithPaitHandler(object):
            def pait_handler(self, content: str) -> str:
                return content

        class WithCallHandler(object):
            def __call__(self, content: str) -> str:
                return content

        def func_handler(content: str) -> str:
            return content

        output_content = "demo"
        assert util.get_pait_handler(WithPaitHandler())(output_content) == output_content
        assert util.get_pait_handler(WithCallHandler())(output_content) == output_content
        assert util.get_pait_handler(func_handler)(output_content) == output_content

    def test_func_sig(self) -> None:
        def demo(a: int, b: str) -> int:
            return 0

        func_sig: util.FuncSig = util.get_func_sig(demo)
        assert func_sig.func == demo
        assert func_sig.sig == inspect.signature(demo)

        assert func_sig == util.get_func_sig(demo)

        sig: inspect.Signature = inspect.signature(demo)
        assert func_sig.param_list == [
            sig.parameters[key]
            for key in sig.parameters
            if sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"
        ]

        def demo1(self, a) -> int:  # type: ignore
            pass

        func_sig = util.get_func_sig(demo1)
        assert len(func_sig.param_list) == 1
        assert func_sig.param_list[0].name == "self"

    def test_is_bounded_func(self) -> None:
        def demo_func(*args: Any, **kwargs: Any) -> None:
            pass

        class Demo(object):
            func_attr = demo_func

            @staticmethod
            def static_method() -> None:
                pass

            @classmethod
            def class_method(cls) -> None:
                pass

            def normal_method(self) -> None:
                pass

        demo = Demo()
        assert util.is_bounded_func(Demo.static_method) is False
        assert util.is_bounded_func(Demo.class_method) is True
        assert util.is_bounded_func(Demo.normal_method) is False
        assert util.is_bounded_func(demo.static_method) is False
        assert util.is_bounded_func(demo.class_method) is True
        assert util.is_bounded_func(demo.normal_method) is True


class AnyStringWith(str):
    def __eq__(self, other: Any) -> bool:
        return self in other


class StringNotIn(str):
    def __eq__(self, other: Any) -> bool:
        return self not in other


class Demo:
    pass


class FakeRequestResourceField(field.BaseRequestResourceField):
    pass


class TestGenTipExc:
    def test_raise_and_tip_param_value_is_empty(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.util._gen_tip.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b",
            inspect.Parameter.POSITIONAL_ONLY,
            annotation=str,
        )
        util._gen_tip.gen_tip_exc(Demo(), Exception(), parameter)
        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))
        patch.assert_called_with(AnyStringWith("b: <class 'str'>"))

    def test_raise_and_tip_param_value_is_pait_field(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.util._gen_tip.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=FakeRequestResourceField.i()
        )
        util._gen_tip.gen_tip_exc(Demo(), Exception(), parameter)

        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))
        patch.assert_called_with(AnyStringWith("b: <class 'str'> = FakeRequestResourceField"))

    def test_raise_and_tip_param_value_is_not_pait_field(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.util._gen_tip.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=""
        )
        util._gen_tip.gen_tip_exc(Demo(), Exception(), parameter)
        patch.assert_called_with(StringNotIn("alias"))
        patch.assert_called_with(AnyStringWith("class: `Demo`  attributes error"))
        patch.assert_called_with(AnyStringWith("b: <class 'str'> = "))

    def test_raise_and_exception_is_tip_exception(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.util._gen_tip.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=""
        )
        util._gen_tip.gen_tip_exc(Demo(), TipException("demo", Exception()), parameter)
        assert patch.call_args is None

    def test_raise_and_tip_exception_class_is_none(self, mocker: MockFixture) -> None:
        patch = mocker.patch("pait.util._gen_tip.logging.debug")
        parameter: inspect.Parameter = inspect.Parameter(
            "b", inspect.Parameter.POSITIONAL_ONLY, annotation=str, default=""
        )
        util._gen_tip.gen_tip_exc(Demo(), Exception(), parameter, tip_exception_class=None)
        assert patch.call_args is None


class TestLazyProperty:
    async def test_lazy_property_fun(self) -> None:
        @util.LazyProperty(self)
        def _demo(a: int, b: int) -> int:
            return a + b

        @util.LazyProperty(self)
        async def _async_demo(a: int, b: int) -> int:
            return a + b

        assert _demo(1, 3) == _demo(1, 4)
        assert await _async_demo(1, 5) == await _async_demo(1, 6)
        assert _demo(2, 1) != await _async_demo(2, 1)

    async def test_lazy_property_class(self) -> None:
        class Demo(object):
            @util.LazyProperty()
            def demo_func(self, a: int, b: int) -> int:
                return a + b

            @util.LazyProperty()
            async def async_demo_func(self, a: int, b: int) -> int:
                return a + b

        demo: Demo = Demo()
        demo1: Demo = Demo()
        assert demo.demo_func(1, 2) == demo.demo_func(1, 3)
        assert demo1.demo_func(1, 4) == demo1.demo_func(1, 5)

        assert await demo.async_demo_func(2, 2) == await demo.async_demo_func(2, 3)
        assert await demo1.async_demo_func(2, 4) == await demo1.async_demo_func(2, 5)

        assert demo.demo_func(3, 1) != demo1.demo_func(3, 1)
        assert await demo.async_demo_func(3, 2) != await demo1.async_demo_func(3, 2)


class TestTypes:
    def test_parse_typing(self) -> None:
        assert [dict] == util.parse_typing(dict)
        assert [list] == util.parse_typing(List)
        assert [list] == util.parse_typing(List[str])
        assert [dict] == util.parse_typing(Dict)
        assert [set] == util.parse_typing(typing.Set)
        assert [dict] == util.parse_typing(Union[dict])
        assert [dict] == util.parse_typing(Union[Dict])
        assert [dict] == util.parse_typing(Union[Dict[str, Any]])
        assert [dict] == util.parse_typing(typing.AsyncIterator[Dict])
        assert [dict] == util.parse_typing(typing.Iterator[Dict])
        assert [dict] == util.parse_typing(typing.Generator[Dict, None, None])
        assert [dict] == util.parse_typing(typing.AsyncGenerator[Dict, None])
        assert [tuple] == util.parse_typing(typing.Tuple[str, int])

        typed_dict_test_list = [
            (typing_extensions.TypedDict, typing_extensions.is_typeddict),  # type: ignore[attr-defined]
        ]
        try:
            from typing import TypedDict, is_typeddict  # type: ignore[attr-defined]

            typed_dict_test_list.append((TypedDict, is_typeddict))
        except ImportError:
            pass

        for _TypedDict, _is_typeddict in typed_dict_test_list:
            if inspect.isfunction(_TypedDict):
                assert [dict] == util.parse_typing(_TypedDict("demo"), _is_typeddict)
            else:
                assert [dict] == util.parse_typing(_TypedDict, _is_typeddict)
        # multi value
        assert [dict, str, int] == util.parse_typing(Union[Dict, str, int])
        assert [dict, type(None)] == util.parse_typing(Optional[Dict])
        assert [dict, type(None)] == util.parse_typing(Optional[dict])
        # Relatively rarely used scenes
        assert [int] == util.parse_typing(typing.NewType("UserId", int))
        assert [int] == util.parse_typing(typing.Callable[[], int])
        assert [int] == util.parse_typing(typing.Callable[[], typing.Awaitable[int]])
        s = typing.TypeVar("s", int, str)
        assert [int, str] == util.parse_typing(s)
        assert [str] == util.parse_typing(typing_extensions.Literal["a", "b"])
        assert [str] == util.parse_typing(typing_extensions.LiteralString)

        class Demo:
            pass

        assert [int] == util.parse_typing(typing_extensions.Annotated[int, Demo])
        # Unresolved type, returned directly
        from pait.util._types import _TYPING_NOT_PARSE_TYPE_SET

        for i in _TYPING_NOT_PARSE_TYPE_SET:
            assert [i] == util.parse_typing(i)

    def test_is_type(self) -> None:
        assert util.is_type(str, Union[str, int])
        assert util.is_type(List[str], List[str])
        assert not util.is_type(str, List[str])


class TestUtil:
    def test_get_func_param_kwargs(self) -> None:
        kwargs_dict = {"a": 1, "b": 2, "c": 3}

        def demo1(a, b):  # type: ignore
            pass

        assert {"a": 1, "b": 2} == util.get_func_param_kwargs(demo1, kwargs_dict)

        def demo2(a, b, **kwargs):  # type: ignore
            pass

        assert {"a": 1, "b": 2, "c": 3} == util.get_func_param_kwargs(demo2, kwargs_dict)

    def test_create_factory(self) -> None:
        def demo(a: int, b: int) -> int:
            return a + b

        assert util.create_factory(demo)(1, 2)() == 3

    def test_partial_wrapper(self) -> None:
        def demo(a: int, b: int = 1, c: int = 2) -> int:
            return a + b + c

        assert demo(1) == 4
        demo1 = util.partial_wrapper(demo, b=3)
        assert demo1(1) == 6
        demo2 = util.partial_wrapper(demo, b=3, c=4)
        assert demo2(1) == 8

    def test_example_value_handle(self) -> None:
        class DemoEnum(enum.Enum):
            a = 1
            b = 2

        assert util.example_value_handle(DemoEnum.a) == 1

        def demo() -> int:
            return 1

        assert util.example_value_handle(demo) == 1

    def test_get_real_annotation(self) -> None:
        class Demo:
            class SubDemo:
                pass

            a: SubDemo

        assert "test_get_real_annotation.<locals>.Demo.SubDemo'" in str(
            util.get_real_annotation(Demo.__annotations__["a"], Demo)
        )

        # support postponed annotations
        class Demo1:
            class SubDemo1:
                pass

            a: "SubDemo1"

        assert "test_get_real_annotation.<locals>.Demo1.SubDemo1'" in str(
            util.get_real_annotation(Demo1.__annotations__["a"], Demo1)
        )

        # Closures
        def demo2() -> None:
            class Demo2:
                class SubDemo2:
                    pass

                a: "SubDemo2"

            assert ("test_get_real_annotation.<locals>.demo2.<locals>.Demo2.SubDemo2") in str(
                util.get_real_annotation(Demo2.__annotations__["a"], Demo2)
            )

        demo2()

    def test_get_pydantic_annotation(self) -> None:
        class SubDemo1(BaseModel):
            a: int = Field()

        class SubDemo2(BaseModel):
            b: conint(ge=0) = Field(default=0)  # type: ignore[valid-type]
            c: constr(min_length=0) = Field(default="")  # type: ignore[valid-type]

        class Demo(SubDemo1, SubDemo2):
            pass

        assert util.get_pydantic_annotation("a", Demo) == int
        assert util.get_pydantic_annotation("b", Demo) == int
        assert util.get_pydantic_annotation("c", Demo) == str

    def test_get_pait_response_model(self) -> None:
        from example.common.response_model import TextRespModel, UserSuccessRespModel2, UserSuccessRespModel3
        from pait.model.response import JsonResponseModel

        class DemoTestRespModel(TextRespModel):
            pass

        # Find target pait response class
        assert UserSuccessRespModel3 == util.get_pait_response_model(
            [DemoTestRespModel, UserSuccessRespModel3], JsonResponseModel
        )

        assert UserSuccessRespModel2 == util.get_pait_response_model([UserSuccessRespModel2])

    def test_gen_example_value_from_python(self) -> None:
        assert util.gen_example_value_from_python(
            {
                "a": 3,
                "b": "xxx",
                "c": False,
                "d": {
                    "a": [1, 2, 3],
                    "b": {"c": 3, "d": 4},
                },
            }
        ) == {"a": 0, "b": "", "c": True, "d": {"a": [], "b": {"c": 0, "d": 0}}}

    def test_gen_example_value_from_type(self) -> None:
        from typing_extensions import TypedDict

        class Demo(TypedDict):
            class SubDemo(TypedDict):  # type: ignore[misc]
                a: bool
                b: float

            a: int
            b: str
            c: bool
            d: SubDemo

        assert util.gen_example_value_from_type(Demo) == {"a": 0, "b": "", "c": True, "d": {"a": True, "b": 0.0}}
        assert util.gen_example_value_from_type(Optional[int]) == 0  # type: ignore[arg-type]
        assert util.gen_example_value_from_type(Generator[int, None, None]) == 0

    def test_gen_example_value_from_pydantic_model(self) -> None:
        class SexEnum(enum.Enum):
            man = "man"
            woman = "woman"

        class Empty(object):
            pass

        class Demo(BaseModel):
            a: int = Field()
            b: str = Field(example="mock")
            c: bool = Field(alias="alias_c")
            d: float = Field(default=2.1)
            e: int = Field(default_factory=lambda: 10)
            f: datetime.date = Field()
            g: SexEnum = Field()
            h: List[str] = Field()
            i: Dict[str, List[int]] = Field()

        assert util.gen_example_dict_from_pydantic_base_model(Demo) == {
            "a": 0,
            "b": "mock",
            "alias_c": True,
            "d": 2.1,
            "e": 10,
            "f": datetime.date.today(),
            "g": "man",
            "h": [""],
            "i": {},
        }

        class Demo1(BaseModel):
            a: int = Field(example=1)
            b: int = Field(new_example_column=2)

        assert util.gen_example_dict_from_pydantic_base_model(Demo1, example_column_name="new_example_column") == {
            "a": 0,
            "b": 2,
        }

    def test_gen_example_value_from_schema(self) -> None:
        assert util.gen_example_dict_from_schema({}) == {}

        class SexEnum(enum.Enum):
            man = "man"
            woman = "woman"

        class Empty(object):
            pass

        class Demo(BaseModel):
            a: int = Field()
            b: str = Field(example="mock")
            c: bool = Field(alias="alias_c")
            d: float = Field(default=2.1)
            e: int = Field(default_factory=lambda: 10)
            f: datetime.date = Field()
            g: SexEnum = Field()
            h: List[str] = Field()
            i: Dict[str, List[int]] = Field()

        assert util.gen_example_dict_from_schema(_pydanitc_adapter.model_json_schema(Demo)) == {
            "a": 0,
            "b": "mock",
            "alias_c": True,
            "d": 2.1,
            "e": 0,
            "f": "",
            "g": "man",
            "h": [],
            "i": {},
        }
        assert (
            util.gen_example_json_from_schema(_pydanitc_adapter.model_json_schema(Demo))
            == '{"a": 0, "b": "mock", "alias_c": true, "d": 2.1, "e": 0, "f": "", "g": "man", "h": [], "i": {}}'
        )
