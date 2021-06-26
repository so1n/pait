import inspect
import sys
from concurrent import futures
from dataclasses import dataclass
from typing import Any, Callable, Dict, ForwardRef, List, Optional, Tuple, Type, get_type_hints

from pydantic import BaseModel, create_model

from pait.g import config


class UndefinedType:
    def __repr__(self) -> str:
        return "PaitUndefined"


# pait undefined flag
Undefined: UndefinedType = UndefinedType()


class LazyProperty:
    """Cache field computing resources
    >>> class Demo:
    ...     @LazyProperty
    ...     def value(self, value):
    ...         return value * value
    """

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            class_ = args[0]
            future: Optional[futures.Future] = getattr(
                class_, f"{self.__class__.__name__}_{func.__name__}_future", None
            )
            if not future:
                future = futures.Future()
                result: Any = func(*args, **kwargs)
                future.set_result(result)
                setattr(class_, f"{self.__class__.__name__}_{func.__name__}_future", future)
                return result
            return future.result()

        return wrapper


def create_pydantic_model(
    annotation_dict: Dict[str, Tuple[Type, Any]], class_name: str = "DynamicModel"
) -> Type[BaseModel]:
    """pydantic create_model helper
    if use create_model('DynamicModel', **annotation_dict), mypy will tip error
    """
    return create_model(
        class_name,
        __config__=None,
        __base__=None,
        __module__="pydantic.main",
        __validators__=None,
        **annotation_dict,
    )


def gen_example_json_from_schema(schema_dict: Dict[str, Any], definition_dict: Optional[dict] = None) -> Dict[str, Any]:
    gen_dict: Dict[str, Any] = {}
    property_dict: Dict[str, Any] = schema_dict["properties"]
    if not definition_dict:
        _definition_dict: dict = schema_dict.get("definitions", {})
    else:
        _definition_dict = definition_dict
    for key, value in property_dict.items():
        if "items" in value and value["type"] == "array":
            if "$ref" in value["items"]:
                model_key: str = value["items"]["$ref"].split("/")[-1]
                gen_dict[key] = [gen_example_json_from_schema(_definition_dict.get(model_key, {}), _definition_dict)]
            else:
                gen_dict[key] = []
        elif "$ref" in value:
            model_key = value["$ref"].split("/")[-1]
            gen_dict[key] = gen_example_json_from_schema(_definition_dict.get(model_key, {}), _definition_dict)
        else:
            if "default" in value:
                gen_dict[key] = value["default"]
            else:
                if value["type"] not in config.json_type_default_value_dict:
                    raise KeyError(f"Can not found type: {key} in json type")
                gen_dict[key] = config.json_type_default_value_dict[value["type"]]
    return gen_dict


@dataclass()
class FuncSig:
    """func inspect.Signature model"""

    func: Callable
    sig: "inspect.Signature"
    param_list: List["inspect.Parameter"]


def get_func_sig(func: Callable) -> FuncSig:
    """get func inspect.Signature model"""
    sig: inspect.Signature = inspect.signature(func)
    param_list: List[inspect.Parameter] = []
    for key in sig.parameters:
        if not (sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == "self"):
            continue
        parameter: inspect.Parameter = sig.parameters[key]
        if isinstance(parameter.annotation, str):
            value: ForwardRef = ForwardRef(parameter.annotation, is_argument=False)
            setattr(
                parameter, "_annotation", value._evaluate(sys.modules[func.__module__].__dict__, None)  # type: ignore
            )
        param_list.append(parameter)

    # return_param = sig.return_annotation
    return FuncSig(func=func, sig=sig, param_list=param_list)


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
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
