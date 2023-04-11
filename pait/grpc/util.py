import inspect
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel

from pait.util import create_pydantic_model

_T = TypeVar("_T", bound=Type[BaseModel])


def _rebuild_message_by_exclude_column_name(
    pydantic_model: _T,
    route_func_name: str,
    exclude_column_name: list,
) -> _T:
    raw_pydantic_model: Type[BaseModel] = pydantic_model
    annotation_dict: Dict[str, Tuple[Type, Any]] = {}
    pydantic_validators: Dict[str, classmethod] = {}
    for column_name, model_field in raw_pydantic_model.__fields__.items():
        if column_name in exclude_column_name:
            continue
        annotation_dict[column_name] = (model_field.type_, model_field.field_info)
        for validators in raw_pydantic_model.__validators__.get(column_name, []):  # type: ignore
            pydantic_validators[validators.func.__name__] = validators
    return create_pydantic_model(  # type: ignore[return-value]
        annotation_dict=annotation_dict,
        class_name=(raw_pydantic_model.__name__ + f"{''.join([i.title() for i in route_func_name.split('_')])}Rebuild"),
        pydantic_base=raw_pydantic_model.__base__,  # type: ignore
        pydantic_module=raw_pydantic_model.__module__,
    )


def rebuild_message(
    pydantic_model: Type[BaseModel],
    route_func_name: str,
    exclude_column_name: Optional[list] = None,
    nested: Optional[list] = None,
) -> Type[BaseModel]:
    if not exclude_column_name and not nested:
        return pydantic_model
    if exclude_column_name:
        pydantic_model = _rebuild_message_by_exclude_column_name(pydantic_model, route_func_name, exclude_column_name)
    elif nested:
        for index, column in enumerate(nested):
            pydantic_model = pydantic_model.__fields__[column].outer_type_
            if not (inspect.isclass(pydantic_model) and issubclass(pydantic_model, BaseModel)):
                raise TypeError(f"Parse {route_func_name} pydantic_model error: {pydantic_model}")
    return pydantic_model


def rebuild_message_type(
    pydantic_model: _T,
    route_func_name: str,
    exclude_column_name: Optional[list] = None,
    nested: Optional[list] = None,
) -> Type:
    if not exclude_column_name and not nested:
        return pydantic_model
    if exclude_column_name:
        pydantic_model = _rebuild_message_by_exclude_column_name(pydantic_model, route_func_name, exclude_column_name)
    elif nested:
        for index, column in enumerate(nested):
            pydantic_model = pydantic_model.__fields__[column].outer_type_
            if not (inspect.isclass(pydantic_model) and issubclass(pydantic_model, BaseModel)):
                continue
    return pydantic_model


def rebuild_dict(
    user_dict: dict,
    exclude_column_name: Optional[list] = None,
    nested: Optional[list] = None,
) -> Any:
    if not exclude_column_name and not nested:
        return user_dict
    if exclude_column_name:
        user_dict = {k: v for k, v in user_dict.items() if k not in exclude_column_name}
    elif nested:
        for column in nested:
            user_dict = user_dict[column]
    return user_dict
