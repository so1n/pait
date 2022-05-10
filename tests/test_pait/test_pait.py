import pytest

from pait import field


class TestField:
    def test_call_base_field(self) -> None:
        with pytest.raises(RuntimeError):
            field.BaseField()

    def test_error_inherit_base_field(self) -> None:
        class Demo(field.Body):
            pass

        with pytest.raises(RuntimeError):
            Demo()
