import inspect
from typing import Any, List, Type

from pydantic import BaseModel

from pait import field, util


class TestUtil:
    def test_create_pydantic_model(self) -> None:
        pydantic_model_class: Type[BaseModel] = util.create_pydantic_model({"a": (int, ...), "b": (str, ...)})
        pydantic_model = pydantic_model_class(a=1, b="a")
        assert pydantic_model.dict() == {"a": 1, "b": "a"}

    def test_func_sig(self) -> None:
        def demo(a: int, b: str) -> int:
            pass

        func_sig: util.FuncSig = util.get_func_sig(demo)
        assert func_sig.func == demo
        assert func_sig.sig == inspect.signature(demo)
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

    def test_get_parameter_list_from_class(self) -> None:
        value: Any = field.Body.i()

        class Demo1(object):
            pass

        class Demo2(object):
            a: int
            b: str = ""
            c: str = value

        assert [] == util.get_parameter_list_from_class(Demo1)
        result: List["inspect.Parameter"] = util.get_parameter_list_from_class(Demo2)
        assert len(result) == 1
        assert result[0].name == "c"
        assert result[0].annotation == str
        assert result[0].default == value
