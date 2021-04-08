import importlib
import pytest
import sys
from unittest import mock

from pytest_mock import MockFixture
from pait import app, field, model
from example import param_verify


class TestField:
    def test_call_base_field(self) -> None:
        with pytest.raises(RuntimeError):
            field.BaseField()

    def test_error_inherit_base_field(self) -> None:
        class Demo(field.Body):
            pass

        with pytest.raises(RuntimeError):
            Demo()


class TestPaitBaseModel:
    def test_pait_base_model(self) -> None:
        class Demo(model.PaitBaseModel):
            a: int
            b: str

            def __init__(self, a: int, b: str):
                self.a = a
                self.b = b

        assert Demo.__annotations__ == Demo.to_pydantic_model().__annotations__
        assert Demo.schema() == Demo.to_pydantic_model().schema()
        assert Demo(a=1, b="1").dict() == dict(a=1, b="1")
