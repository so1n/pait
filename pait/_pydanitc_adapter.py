from typing import Any, Type

from any_api.util import pydantic_adapter as _any_api_pydantic_adapter
from pydantic import BaseModel

from pait.exceptions import ValidationError as _ValidationError

__all__ = ["PydanticUndefinedType", "PydanticUndefined", "is_v1", "ConfigDict"]

is_v1 = _any_api_pydantic_adapter.is_v1
ConfigDict = _any_api_pydantic_adapter.ConfigDict
model_fields = _any_api_pydantic_adapter.model_fields
VERSION = _any_api_pydantic_adapter.VERSION
model_json_schema = _any_api_pydantic_adapter.model_json_schema
get_field_info = _any_api_pydantic_adapter.get_field_info
model_validator = _any_api_pydantic_adapter.model_validator
model_dump = _any_api_pydantic_adapter.model_dump

if _any_api_pydantic_adapter.is_v1:
    from pydantic import BaseConfig
    from pydantic.error_wrappers import ValidationError
    from pydantic.fields import FieldInfo, ModelField
    from pydantic.fields import Undefined as PydanticUndefined
    from pydantic.schema import get_annotation_from_field_info

    PydanticUndefinedType = type(PydanticUndefined)

    def validate_value_by_field(
        value: Any,
        value_name: str,
        annotation: type,
        field_info: FieldInfo,
        request_param: str,
        base_model: Type[BaseModel] = BaseModel,
    ) -> Any:
        _model_field = ModelField(
            name=value_name,
            type_=get_annotation_from_field_info(annotation, field_info, value_name),
            model_config=BaseConfig,
            field_info=field_info,
            class_validators={},
            # Since the corresponding value has already been processed, there is no need to process it again
            # default: Any = None,
            # default_factory: Optional[NoArgAnyCallable] = None,
            # required: 'BoolUndefined' = Undefined,
            # final: bool = False,
            # alias: Optional[str] = None,
        )
        ok_value, e = _model_field.validate(value, {}, loc=(request_param, value_name))
        if e:
            raise _ValidationError(
                [{"type": e.exc.__class__.__name__, "loc": e._loc, "msg": "", "input": value, "ctx": {"error": ""}}],
                base_model,
            )
        return ok_value

    def get_field_extra(field: FieldInfo) -> dict:
        return field.extra

else:
    from typing import Any, Dict, List, Sequence, Tuple, Union

    from pydantic import BaseModel, TypeAdapter, ValidationError
    from pydantic.fields import FieldInfo, PydanticUndefined
    from typing_extensions import Annotated

    PydanticUndefinedType = type(PydanticUndefined)

    class ErrorWrapper(Exception):
        pass

    def _normalize_errors(errors: Sequence[Any]) -> List[Dict[str, Any]]:
        use_errors: List[Any] = []
        for error in errors:
            if isinstance(error, ErrorWrapper):
                new_errors = ValidationError(errors=[error], model=BaseModel).errors()  # type: ignore[call-arg]
                use_errors.extend(new_errors)
            elif isinstance(error, list):
                use_errors.extend(_normalize_errors(error))
            else:
                use_errors.append(error)
        return use_errors

    def _regenerate_error_with_loc(
        *, errors: Sequence[Any], loc_prefix: Tuple[Union[str, int], ...]
    ) -> List[Dict[str, Any]]:
        updated_loc_errors: List[Any] = [
            {**err, "loc": loc_prefix + err.get("loc", ())} for err in _normalize_errors(errors)
        ]

        return updated_loc_errors

    def validate_value_by_field(
        value: Any,
        value_name: str,
        annotation: type,
        field_info: FieldInfo,
        request_param: str,
        base_model: Type[BaseModel] = BaseModel,
    ) -> Any:
        _type_adapter: TypeAdapter[Any] = TypeAdapter(Annotated[annotation, field_info])
        try:
            return _type_adapter.validate_python(value, from_attributes=True)
        except ValidationError as exc:
            raise _ValidationError(
                _regenerate_error_with_loc(errors=exc.errors(), loc_prefix=(request_param, value_name)), base_model
            )

    def get_field_extra(field: FieldInfo) -> dict:
        return field.json_schema_extra or {}
