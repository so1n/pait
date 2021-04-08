import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, get_type_hints
from pydantic import BaseConfig, BaseModel, create_model


class UndefinedType:
    def __repr__(self) -> str:
        return "PaitUndefined"


Undefined: UndefinedType = UndefinedType()


def create_pydantic_model(annotation_dict: Dict[str, Tuple[Type, Any]]) -> Type[BaseModel]:
    """if use create_model('DynamicModel', **annotation_dict), mypy will tip error"""
    return create_model(
        "DynamicModel",
        __config__=None,
        __base__=None,
        __module__="pydantic.main",
        __validators__=None,
        **annotation_dict
    )


@dataclass()
class FuncSig:
    func: Callable
    sig: "inspect.Signature"
    param_list: List["inspect.Parameter"]


def get_func_sig(func: Callable) -> FuncSig:
    sig: inspect.Signature = inspect.signature(func)
    param_list: List[inspect.Parameter] = [
        sig.parameters[key]
        for key in sig.parameters
        if sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"
    ]
    # return_param = sig.return_annotation
    return FuncSig(func=func, sig=sig, param_list=param_list)


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    parameter_list: List["inspect.Parameter"] = []
    if hasattr(cbv_class, "__annotations__"):
        for param_name, param_annotation in get_type_hints(cbv_class).items():
            parameter: "inspect.Parameter" = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=getattr(cbv_class, param_name, Undefined),
                annotation=param_annotation,
            )
            parameter_list.append(parameter)
    return parameter_list
