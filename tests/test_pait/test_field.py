import pytest

from pait import _pydanitc_adapter, field
from pait.field.request_resource import PydanticUndefined


class TestField:
    def test_is_pait_field(self) -> None:
        assert field.is_pait_field(field.Query.i())

    def test_is_pait_field_class(self) -> None:
        assert field.is_pait_field_class(field.Query)

    def test_multi_default_param(self) -> None:
        with pytest.raises(ValueError):
            field.BaseRequestResourceField(default=1, default_factory=lambda: 1)
        with pytest.raises(ValueError):
            field.BaseRequestResourceField(default=1, not_value_exception_func=lambda x: Exception())

        with pytest.raises(ValueError):
            field.BaseRequestResourceField(default_factory=lambda: 1, not_value_exception_func=lambda x: Exception())

    def test_request_value_handler(self) -> None:
        normal_field = field.BaseRequestResourceField()
        with_default_field = field.BaseRequestResourceField(default=1)
        with_default_factory_field = field.BaseRequestResourceField(default_factory=lambda: 1)
        normal_field.set_request_key("a")
        with_default_field.set_request_key("a")
        with_default_factory_field.set_request_key("a")
        request_dict: dict = {}

        assert normal_field.request_value_handle(request_dict) is PydanticUndefined
        assert with_default_field.request_value_handle(request_dict) == 1
        assert with_default_factory_field.request_value_handle(request_dict) == 1

    def test_init_param_error(self) -> None:
        with pytest.raises(ValueError):
            field.BaseRequestResourceField(regex="a", pattern="a")
        with pytest.raises(ValueError):
            field.BaseRequestResourceField(alias=1)  # type: ignore
        if _pydanitc_adapter.is_v1:
            with pytest.raises(ValueError):
                field.BaseRequestResourceField(json_schema_extra={"example": 1})
            demo_field = field.BaseRequestResourceField(const=1, pattern="a")  # type: ignore
            assert demo_field.const == 1  # type: ignore
            assert demo_field.regex == "a"  # type: ignore
        else:
            assert field.BaseRequestResourceField(regex="a").metadata[0].pattern == "a"

            with pytest.raises(ValueError):
                field.BaseRequestResourceField(max_items=1, max_length=1)
            assert field.BaseRequestResourceField(max_items=1).metadata[0].max_length == 1

            with pytest.raises(ValueError):
                field.BaseRequestResourceField(min_items=1, min_length=1)
            assert field.BaseRequestResourceField(min_items=1).metadata[0].min_length == 1

            with pytest.raises(ValueError):
                field.BaseRequestResourceField(json_schema_extra=lambda x: x.update(), example=1)

            with pytest.raises(ValueError):
                field.BaseRequestResourceField(json_schema_extra=lambda x: x.update(), extra_a=1)

            assert field.BaseRequestResourceField(json_schema_extra={"extra_a": 1}, example=1).json_schema_extra == {
                "extra_a": 1,
                "example": 1,
            }

    def test_path_check_init_param(self) -> None:
        with pytest.raises(ValueError):
            field.Path.i(default=1)
        with pytest.raises(ValueError):
            field.Path.i(default_factory=lambda: 1)

    def test_get_link(self) -> None:
        from example.common.response_model import link_login_token_model

        assert field.BaseRequestResourceField().links is None
        assert (
            field.BaseRequestResourceField(links=link_login_token_model).links.openapi_runtime_expr  # type: ignore
            is link_login_token_model.openapi_runtime_expr
        )
