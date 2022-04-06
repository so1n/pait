import inspect
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import wraps
from json import JSONEncoder
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    ForwardRef,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from pydantic import BaseModel
from pydantic.fields import Undefined, UndefinedType

from pait.field import BaseField, Depends, is_pait_field
from pait.model.template import TemplateVar

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

from ._types import ParseTypeError, parse_typing

if TYPE_CHECKING:
    from pait.model.response import PaitBaseResponseModel

ignore_pre_check: bool = bool(os.environ.get("IGNORE_PRE_CHECK", False))
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

python_type_default_value_dict: Dict[type, Any] = {
    bool: True,
    float: 0.0,
    int: 0,
    str: "",
    list: [],
    tuple: (),
    dict: {},
    datetime: datetime.fromtimestamp(0),
    Decimal: Decimal("0.0"),
}


P = ParamSpec("P")
R_T = TypeVar("R_T")


def create_factory(func: Callable[P, R_T]) -> Callable[P, R_T]:  # type: ignore
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_T:  # type: ignore
        return lambda: func(*args, **kwargs)  # type: ignore

    return wrapper


def example_value_handle(example_value: Any) -> Any:
    if getattr(example_value, "__call__", None):
        example_value = example_value()
    elif isinstance(example_value, Enum):
        example_value = example_value.value
    elif isinstance(example_value, TemplateVar):
        example_value = example_value.get_value_from_template_context()
    return example_value


def get_real_annotation(annotation: Union[Type, str], target_obj: Any) -> Type:
    if not isinstance(annotation, str):
        return annotation
    if inspect.isclass(target_obj) and annotation in target_obj.__dict__:
        new_annotation: Type = target_obj.__dict__[annotation]
    else:
        # get real type
        value: ForwardRef = ForwardRef(annotation, is_argument=False)
        new_annotation = value._evaluate(sys.modules[target_obj.__module__].__dict__, None)  # type: ignore
        if not new_annotation:
            raise RuntimeError(f"get real annotation from {target_obj} fail")  # pragma: no cover
    return new_annotation


def get_pydantic_annotation(key: str, pydantic_base_model: Type[BaseModel]) -> Type:
    annotation: Type = pydantic_base_model.__annotations__[key]
    annotation = get_real_annotation(annotation, pydantic_base_model)

    if getattr(annotation, "real", None) and annotation != bool:
        # support like pydantic.ConstrainedIntValue
        annotation = annotation.real.__objclass__  # type: ignore
    return annotation


def get_pait_response_model(
    response_model_list: List[Type["PaitBaseResponseModel"]],
    target_pait_response_class: Optional[Type["PaitBaseResponseModel"]] = None,
    find_core_response_model: bool = False,
) -> Type["PaitBaseResponseModel"]:
    if target_pait_response_class:
        core_response_list: List[Type["PaitBaseResponseModel"]] = [
            i for i in response_model_list if i.is_core and issubclass(i, target_pait_response_class)
        ]
    else:
        core_response_list = [i for i in response_model_list if i.is_core]
    if find_core_response_model:
        if len(core_response_list) != 1:
            raise RuntimeError("Multiple pait response models were found")
        return core_response_list[0]
    else:
        return (core_response_list or response_model_list)[0]


def gen_example_value_from_python(obj: Any) -> Any:
    if isinstance(obj, dict):
        new_dict: dict = {}
        for key, value in obj.items():
            new_dict[key] = gen_example_value_from_python(value)
        return new_dict
    else:
        return python_type_default_value_dict.get(type(obj), obj)


def gen_example_dict_from_pydantic_base_model(
    pydantic_base_model: Type[BaseModel], use_example_value: bool = True
) -> dict:
    gen_dict: Dict[str, Any] = {}
    for key, model_field in pydantic_base_model.__fields__.items():
        if use_example_value:
            example_value: Any = model_field.field_info.extra.get("example", Undefined)
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

            if issubclass(annotation, BaseModel):
                gen_dict[key] = gen_example_dict_from_pydantic_base_model(annotation)
            else:
                try:
                    parse_typing_result: Union[List[Type[Any]], Type] = parse_typing(annotation)
                    if isinstance(parse_typing_result, list):
                        real_type: Type = parse_typing_result[0]
                    else:
                        real_type = parse_typing_result
                except ParseTypeError:
                    real_type = annotation
                if issubclass(real_type, Enum):
                    gen_dict[key] = [i for i in real_type.__members__.values()][0].value
                else:
                    gen_dict[key] = python_type_default_value_dict[real_type]
    return gen_dict


def gen_example_dict_from_schema(
    schema_dict: Dict[str, Any],
    definition_dict: Optional[dict] = None,
) -> Dict[str, Any]:
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


def get_parameter_list_from_pydantic_basemodel(pait_model: Type[BaseModel]) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list: Optional[List["inspect.Parameter"]] = getattr(pait_model, "_parameter_list", None)
    if parameter_list is not None:
        return parameter_list
    parameter_list = []
    for key, model_field in pait_model.__fields__.items():
        if not is_pait_field(model_field.field_info):
            raise TypeError(f"{model_field.field_info} must instance {BaseField} or {Depends}")

        parameter = inspect.Parameter(
            key,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.field_info,
            annotation=get_pydantic_annotation(key, pait_model),
        )
        parameter_list.append(parameter)

    setattr(pait_model, "_parameter_list", parameter_list)
    return parameter_list


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list: Optional[List["inspect.Parameter"]] = getattr(cbv_class, "_parameter_list", None)
    if parameter_list is not None:
        return parameter_list
    parameter_list = []
    if hasattr(cbv_class, "__annotations__"):
        for param_name, param_annotation in get_type_hints(cbv_class).items():
            default: Any = getattr(cbv_class, param_name, Undefined)
            if not is_pait_field(default):
                continue
            parameter: "inspect.Parameter" = inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default,
                annotation=param_annotation,
            )
            parameter_list.append(parameter)
    setattr(cbv_class, "_parameter_list", parameter_list)
    return parameter_list


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return int(obj.timestamp())
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, TemplateVar):
            obj = obj.get_value_from_template_context()
            if isinstance(obj, UndefinedType):
                obj = None
            return obj
        else:
            return super().default(obj)
