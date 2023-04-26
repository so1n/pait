import inspect
import json
import os
import sys
from dataclasses import MISSING
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import wraps
from json import JSONEncoder
from typing import (  # type: ignore
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    ForwardRef,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    _eval_type,
    _GenericAlias,
    get_type_hints,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo, Undefined, UndefinedType
from typing_extensions import is_typeddict

from pait.field import BaseField, Depends, is_pait_field
from pait.types import ParamSpec

from ._types import ParseTypeError, parse_typing

if TYPE_CHECKING:
    from pait.model.response import BaseResponseModel

__all__ = [
    "gen_example_dict_from_pydantic_base_model",
    "gen_example_dict_from_schema",
    "gen_example_json_from_schema",
    "get_parameter_list_from_pydantic_basemodel",
    "get_parameter_list_from_class",
    "http_method_tuple",
    "json_type_default_value_dict",
    "python_type_default_value_dict",
    "get_pait_response_model",
    "example_value_handle",
    "ignore_pre_check",
    "gen_example_value_from_python",
    "get_real_annotation",
    "create_factory",
    "partial_wrapper",
    "R_T",
    "P",
]
ignore_pre_check: bool = bool(os.environ.get("PAIT_IGNORE_PRE_CHECK", False))
http_method_tuple: Tuple[str, ...] = ("get", "post", "head", "options", "delete", "put", "trace", "patch")

json_type_default_value_dict: Dict[str, Any] = {
    "null": None,
    "bool": True,
    "boolean": True,
    "string": "",
    "number": 0.0,
    "float": 0.0,
    "integer": 0,
    "object": {},
    "array": [],
}

python_type_default_value_dict: Dict = {
    bool: True,
    float: 0.0,
    int: 0,
    str: "",
    list: [],
    tuple: (),
    dict: {},
    datetime: datetime.fromtimestamp(0),
    Decimal: Decimal("0.0"),
    Any: {},
}


P = ParamSpec("P")
R_T = TypeVar("R_T")


def create_factory(func: Callable[P, R_T]) -> Callable[P, Callable[[], R_T]]:
    """Create a factory that calls the function (Use the syntax hints provided by PEP 612)"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Callable[[], R_T]:
        return lambda: func(*args, **kwargs)

    return wrapper


def partial_wrapper(func: Callable[P, R_T], **_customer_kwargs: Any) -> Callable[P, R_T]:  # type: ignore
    """with type hints partial"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_T:  # type: ignore
        new_kwargs = _customer_kwargs.copy()
        new_kwargs.update(kwargs)
        return func(*args, **new_kwargs)

    return wrapper


def example_value_handle(example_value: Any) -> Any:
    if isinstance(example_value, Enum):
        example_value = example_value.value
    elif getattr(example_value, "__call__", None):
        example_value = example_value()
    return example_value


def get_real_annotation(annotation: Union[Type, str], target_obj: Any) -> Type:
    """
    get the real annotation from postponed annotations/annotations
    :param annotation: type hints
    :param target_obj: The object on which the annotation resides
    :return: the real annotation

    e.g:
    >>> def demo(a: "int") -> int: pass
    >>> assert int = get_real_annotation(demo.__annotations__["a"], demo)

    >>> class Demo:
    >>>     a: "int"
    >>> assert int = get_real_annotation(Demo.__annotations__["a"], Demo)
    """
    global_dict = sys.modules[target_obj.__module__].__dict__
    if not isinstance(annotation, str):
        # Option["Dict[str, int]"]
        return _eval_type(annotation, global_dict, None)
    if inspect.isclass(target_obj) and annotation in target_obj.__dict__:
        new_annotation: Type = target_obj.__dict__[annotation]
    else:
        # get real type
        value: ForwardRef = ForwardRef(annotation, is_argument=False)

        if sys.version_info >= (3, 9):
            new_annotation = value._evaluate(global_dict, None, frozenset())  # type: ignore
        else:
            new_annotation = value._evaluate(global_dict, None)  # type: ignore
        if not new_annotation:
            raise RuntimeError(f"get real annotation from {target_obj} fail")  # pragma: no cover
    return _eval_type(new_annotation, global_dict, None)


def get_pydantic_annotation(key: str, pydantic_base_model: Type[BaseModel]) -> Type:
    """Get the annotation from BaseModel's properties"""
    annotation: Any = MISSING
    for base in reversed(pydantic_base_model.__mro__):
        ann: Union[str, Type] = base.__dict__.get("__annotations__", {}).get(key, MISSING)
        if ann is not MISSING:
            annotation = ann
            break
    if annotation is MISSING:
        raise RuntimeError(f"get {key}'s annotation from {pydantic_base_model} fail")  # pragma: no cover
    annotation = get_real_annotation(annotation, pydantic_base_model)

    if getattr(annotation, "real", None) and annotation != bool:
        # support like pydantic.ConstrainedIntValue
        annotation = annotation.real.__objclass__  # type: ignore
    return annotation


def get_pait_response_model(
    response_model_list: List[Type["BaseResponseModel"]],
    target_pait_response_class: Optional[Type["BaseResponseModel"]] = None,
) -> Type["BaseResponseModel"]:
    if target_pait_response_class:
        response_model_list = [i for i in response_model_list if issubclass(i, target_pait_response_class)]
    return response_model_list[0]


def gen_example_value_from_python(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: gen_example_value_from_python(value) for key, value in obj.items()}
    else:
        return python_type_default_value_dict.get(type(obj), obj)


def gen_example_value_from_type(value_type: type, example_column_name: str = "example") -> Any:
    """
    Gets the default value for type
    :param value_type: type of the value
    :param example_column_name: Gets sample values from the properties specified by pydantic.FieldInfo
    """
    if is_typeddict(value_type):
        return {k: gen_example_value_from_type(v) for k, v in value_type.__annotations__.items()}
    elif isinstance(value_type, _GenericAlias):
        sub_type: Optional[Type] = None
        try:
            parse_typing_result = parse_typing(value_type)
            # If there is more than one type value, only the first one is used
            real_type: Type = parse_typing_result[0]
            annotation_arg_list: list = getattr(value_type, "__args__", [])
            if annotation_arg_list:
                sub_type_set: Set[Type] = set(annotation_arg_list)
                if len(sub_type_set) == 1:
                    sub_type = sub_type_set.pop()
        except ParseTypeError:
            real_type = value_type
        if real_type is list and sub_type:
            return [gen_example_value_from_type(sub_type, example_column_name=example_column_name)]
        else:
            # if real_type is Option[xxx], sub_type is None
            # so must parse real_type
            return gen_example_value_from_type(real_type, example_column_name=example_column_name)
    elif not inspect.isclass(value_type):
        return python_type_default_value_dict[value_type]
    elif issubclass(value_type, Enum):
        return [i for i in value_type.__members__.values()][0].value
    elif issubclass(value_type, BaseModel):
        return gen_example_dict_from_pydantic_base_model(value_type, example_column_name=example_column_name)
    else:
        return python_type_default_value_dict[value_type]


def gen_example_dict_from_pydantic_base_model(
    pydantic_base_model: Type[BaseModel], example_column_name: str = "example"
) -> dict:
    """
    Gets the default value for pydantic.BaseModel
    :param pydantic_base_model: pydantic.BaseModel
    :param example_column_name: Gets sample values from the properties specified by pydantic.FieldInfo
    """
    gen_dict: Dict[str, Any] = {}
    for key, model_field in pydantic_base_model.__fields__.items():
        if model_field.alias:
            key = model_field.alias
        if example_column_name:
            example_value: Any = model_field.field_info.extra.get(example_column_name, Undefined)
            if not isinstance(example_value, UndefinedType):
                gen_dict[key] = example_value_handle(example_value)
                continue

        if not isinstance(model_field.field_info.default, UndefinedType):
            gen_dict[key] = model_field.field_info.default
        elif model_field.field_info.default_factory and not isinstance(
            model_field.field_info.default_factory, UndefinedType
        ):
            gen_dict[key] = model_field.field_info.default_factory()
        else:
            annotation: Type = get_pydantic_annotation(key, pydantic_base_model)
            gen_dict[key] = gen_example_value_from_type(annotation, example_column_name=example_column_name)
    return gen_dict


def gen_example_dict_from_schema(schema_dict: Dict[str, Any], definition_dict: Optional[dict] = None) -> Dict[str, Any]:
    gen_dict: Dict[str, Any] = {}
    if "properties" not in schema_dict:
        return gen_dict
    property_dict: Dict[str, Any] = schema_dict["properties"]
    if not definition_dict:
        _definition_dict: dict = schema_dict.get("definitions", {})
    else:
        _definition_dict = definition_dict
    for key, value in property_dict.items():
        if "items" in value and value["type"] == "array":
            if "$ref" in value["items"]:
                model_key: str = value["items"]["$ref"].split("/")[-1]
                gen_dict[key] = [gen_example_dict_from_schema(_definition_dict.get(model_key, {}), _definition_dict)]
            else:
                gen_dict[key] = []
        elif "$ref" in value:
            model_key = value["$ref"].split("/")[-1]
            gen_dict[key] = gen_example_dict_from_schema(_definition_dict.get(model_key, {}), _definition_dict)
        else:
            if "example" in value:
                gen_dict[key] = example_value_handle(value["example"])
            elif "default" in value:
                gen_dict[key] = value["default"]
            else:
                if "type" in value:
                    if value["type"] not in json_type_default_value_dict:
                        raise KeyError(f"Can not found type: {key} in json type")
                    gen_dict[key] = json_type_default_value_dict[value["type"]]
                else:
                    gen_dict[key] = "object"
            if isinstance(gen_dict[key], Enum):
                gen_dict[key] = gen_dict[key].value
    return gen_dict


def gen_example_json_from_schema(schema_dict: Dict[str, Any], cls: Optional[Type[JSONEncoder]] = None) -> str:
    return json.dumps(gen_example_dict_from_schema(schema_dict), cls=cls)


def get_parameter_list_from_pydantic_basemodel(
    pait_model: Type[BaseModel], default_field_class: Optional[Type[BaseField]] = None
) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    key = f"_parameter_list:{default_field_class}"
    parameter_list: Optional[List["inspect.Parameter"]] = getattr(pait_model, key, None)
    if parameter_list is not None:
        return parameter_list
    parameter_list = []
    for key, model_field in pait_model.__fields__.items():
        field: FieldInfo = model_field.field_info
        if not is_pait_field(field):
            if not default_field_class:
                raise TypeError(  # pragma: no cover
                    f"{field.__class__} must instance {BaseField} or {Depends} by model {pait_model}"
                )
            field = default_field_class.from_pydantic_field(field)

            if getattr(field, "alias", None) is None:
                field.request_key = key
        parameter = inspect.Parameter(
            key,
            inspect.Parameter.POSITIONAL_ONLY,
            default=field,
            annotation=get_pydantic_annotation(key, pait_model),
        )
        parameter_list.append(parameter)

    setattr(pait_model, key, parameter_list)
    return parameter_list


_class_parameter_list_dict: Dict[type, List["inspect.Parameter"]] = {}


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list: Optional[List["inspect.Parameter"]] = _class_parameter_list_dict.get(cbv_class)
    if parameter_list is not None:
        return parameter_list
    parameter_list = []
    if hasattr(cbv_class, "__annotations__"):
        for param_name, param_annotation in get_type_hints(cbv_class).items():
            default: Any = getattr(cbv_class, param_name, Undefined)
            if not is_pait_field(default):
                continue

            # Optimize parsing speed
            if getattr(default, "alias", None) is None:
                default.request_key = param_name
            parameter: "inspect.Parameter" = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default,
                annotation=param_annotation,
            )
            parameter_list.append(parameter)
    _class_parameter_list_dict[cbv_class] = parameter_list
    return parameter_list
