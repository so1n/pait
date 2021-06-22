import pytest

from pait import field
from pait.model.base_model import PaitBaseModel


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
        class Demo(PaitBaseModel):
            a: int
            b: str

            def __init__(self, a: int, b: str):
                self.a = a
                self.b = b

        assert Demo.__annotations__ == Demo.to_pydantic_model().__annotations__
        assert Demo.schema() == Demo.to_pydantic_model().schema()
        assert Demo(a=1, b="1").dict() == dict(a=1, b="1")
