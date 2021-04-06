import inspect
import pytest
from typing import Type
from pydantic import BaseModel
from pait import util


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
