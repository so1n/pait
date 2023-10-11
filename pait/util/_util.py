import inspect
import json
import os
import sys
from datetime import date, datetime
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
)

from packaging import version
from pydantic import BaseModel
from typing_extensions import is_typeddict

from pait.types import ParamSpec

from .. import _pydanitc_adapter
from ._types import ParseTypeError, parse_typing

if TYPE_CHECKING:
    from pait.model.response import BaseResponseModel

__all__ = [
    "gen_example_dict_from_pydantic_base_model",
    "gen_example_dict_from_schema",
    "gen_example_json_from_schema",
    "gen_example_value_from_type",
    "get_pydantic_annotation",
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
    "get_func_param_kwargs",
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
    date: date.today(),
    Decimal: Decimal("0.0"),
    Any: {},
}


P = ParamSpec("P")
R_T = TypeVar("R_T")


def get_func_param_kwargs(func: Callable, kwargs_dict: dict) -> dict:
    """
    >>> kwargs_dict = {"a": 1, "b": 2, "c": 3}
    >>> def demo1(a, b): pass
    >>> assert {"a": 1, "b": 2} == get_func_param_kwargs(demo1, kwargs_dict)
    >>> def demo2(a, b, **kwargs): pass
    >>> assert {"a": 1, "b": 2, "c": 3} == get_func_param_kwargs(demo2, kwargs_dict)
    """
    new_kwargs_dict: dict = {}
    for k, v in inspect.signature(func).parameters.items():
        if v.kind is v.VAR_KEYWORD:
            return kwargs_dict
        if k in kwargs_dict:
            new_kwargs_dict[k] = kwargs_dict[k]
    return new_kwargs_dict


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
            new_annotation = value._evaluate(global_dict, None, frozenset())  # type: ignore    # pragma: no cover
        else:
            new_annotation = value._evaluate(global_dict, None)  # type: ignore
        if not new_annotation:
            raise RuntimeError(f"get real annotation from {target_obj} fail")  # pragma: no cover
    return _eval_type(new_annotation, global_dict, None)


_is_lt_v_1_10 = version.Version(_pydanitc_adapter.VERSION) < version.Version("1.10")


def get_pydantic_annotation(key: str, pydantic_base_model: Type[BaseModel]) -> Type:
    """Get the annotation from BaseModel's properties"""
    if _is_lt_v_1_10:
        from typing_extensions import get_type_hints

        annotation = get_type_hints(pydantic_base_model)[key]
    else:
        # pydantic version > 1.10
        annotation = _pydanitc_adapter.model_fields(pydantic_base_model)[key].annotation
    annotation = get_real_annotation(annotation, pydantic_base_model)
    if getattr(annotation, "real", None) and annotation != bool:
        # support like pydantic.ConstrainedIntValue
        return annotation.real.__objclass__  # type: ignore
    __base__ = getattr(annotation, "__base__", None)
    if __base__ and getattr(__base__, "__module__", "") == "pydantic.types":
        return annotation.__mro__[2]
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
            real_type = value_type  # pragma: no cover
        if real_type is list and sub_type:
            return [gen_example_value_from_type(sub_type, example_column_name=example_column_name)]
        else:
            # if real_type is Option[xxx], sub_type is None
            # so must parse real_type
            return gen_example_value_from_type(real_type, example_column_name=example_column_name)
    elif not inspect.isclass(value_type):
        return python_type_default_value_dict[value_type]  # pragma: no cover
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
    for key, model_field in _pydanitc_adapter.model_fields(pydantic_base_model).items():
        field_info = _pydanitc_adapter.get_field_info(model_field)

        if model_field.alias:
            real_key = model_field.alias
        else:
            real_key = key
        if example_column_name:
            example_value: Any = _pydanitc_adapter.get_field_extra_dict(field_info).get(
                example_column_name, _pydanitc_adapter.PydanticUndefined
            )
            if example_value is not _pydanitc_adapter.PydanticUndefined:
                gen_dict[real_key] = example_value_handle(example_value)
                continue

        if field_info.default is not _pydanitc_adapter.PydanticUndefined:
            gen_dict[real_key] = field_info.default
        elif field_info.default_factory and field_info.default_factory is not _pydanitc_adapter.PydanticUndefined:
            gen_dict[real_key] = field_info.default_factory()
        else:
            annotation: Type = get_pydantic_annotation(key, pydantic_base_model)
            gen_dict[real_key] = gen_example_value_from_type(annotation, example_column_name=example_column_name)
    return gen_dict


def gen_example_dict_from_schema(
    schema_dict: Dict[str, Any], definition_dict: Optional[dict] = None, definition_key: str = "$defs"
) -> Dict[str, Any]:
    gen_dict: Dict[str, Any] = {}
    if "enum" in schema_dict:
        return schema_dict["enum"][0]
    elif "properties" not in schema_dict:
        return gen_dict
    property_dict: Dict[str, Any] = schema_dict["properties"]
    if not definition_dict:
        _definition_dict: dict = schema_dict.get(definition_key, {})
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
            # if isinstance(gen_dict[key], Enum):
            #     gen_dict[key] = gen_dict[key].value
    return gen_dict


def gen_example_json_from_schema(schema_dict: Dict[str, Any], cls: Optional[Type[JSONEncoder]] = None) -> str:
    return json.dumps(gen_example_dict_from_schema(schema_dict), cls=cls)
