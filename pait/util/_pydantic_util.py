from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type

from pydantic import create_model

if TYPE_CHECKING:
    from pydantic import BaseConfig, BaseModel


__all__ = ["create_pydantic_model"]


def create_pydantic_model(
    annotation_dict: Optional[Dict[str, Tuple[Type, Any]]] = None,
    class_name: str = "DynamicModel",
    pydantic_config: Optional[Type["BaseConfig"]] = None,
    pydantic_base: Optional[Type["BaseModel"]] = None,
    pydantic_module: str = "pydantic.main",
    pydantic_validators: Optional[Dict[str, classmethod]] = None,
) -> Type["BaseModel"]:
    """pydantic self.pait_response_model helper
    if use create_model('DynamicModel', **annotation_dict), mypy will tip error
    """
    return create_model(
        class_name,
        __config__=pydantic_config,
        __base__=pydantic_base,
        __module__=pydantic_module,
        __validators__=pydantic_validators,
        **(annotation_dict or {}),
    )
