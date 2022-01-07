import inspect
import json
import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, get_type_hints

from pydantic import BaseConfig, BaseModel, create_model

from pait.exceptions import PaitBaseException
from pait.field import BaseField, Depends, is_pait_field

from ._func_sig import FuncSig

if TYPE_CHECKING:
    from pait.model.response import PaitBaseResponseModel


class UndefinedType:
    def __repr__(self) -> str:
        return "PaitUndefined"


# pait undefined flag
Undefined: UndefinedType = UndefinedType()

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
    tuple: [],
    datetime: 0,
    Decimal: 0,
}


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


def create_pydantic_model(
    annotation_dict: Dict[str, Tuple[Type, Any]],
    class_name: str = "DynamicModel",
    pydantic_config: Type[BaseConfig] = None,
    pydantic_base: Type[BaseModel] = None,
    pydantic_module: str = "pydantic.main",
    pydantic_validators: Dict[str, classmethod] = None,
) -> Type[BaseModel]:
    """pydantic create_model helper
    if use create_model('DynamicModel', **annotation_dict), mypy will tip error
    """
    return create_model(
        class_name,
        __config__=pydantic_config,
        __base__=pydantic_base,
        __module__=pydantic_module,
        __validators__=pydantic_validators,
        **annotation_dict,
    )


def gen_example_json_from_python(obj: Any) -> Any:
    if isinstance(obj, dict):
        new_dict: dict = {}
        for key, value in obj.items():
            new_dict[key] = gen_example_json_from_python(value)
        return new_dict
    else:
        return python_type_default_value_dict.get(type(obj), obj)


def gen_example_dict_from_schema(schema_dict: Dict[str, Any], definition_dict: Optional[dict] = None) -> Dict[str, Any]:
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
                gen_dict[key] = [gen_example_dict_from_schema(_definition_dict.get(model_key, {}), _definition_dict)]
            else:
                gen_dict[key] = []
        elif "$ref" in value:
            model_key = value["$ref"].split("/")[-1]
            gen_dict[key] = gen_example_dict_from_schema(_definition_dict.get(model_key, {}), _definition_dict)
        else:
            if "example" in value:
                gen_dict[key] = value["example"]
                if inspect.isfunction(gen_dict[key]):
                    gen_dict[key] = gen_dict[key]()
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
        annotation: Type = pait_model.__annotations__[key]
        if getattr(annotation, "real", None):
            # support like pydantic.ConstrainedIntValue
            annotation = annotation.real.__objclass__  # type: ignore
        parameter = inspect.Parameter(
            key,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.field_info,
            annotation=annotation,
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


def gen_tip_exc(_object: Any, exception: "Exception", parameter: Optional[inspect.Parameter] = None) -> Exception:
    """Help users understand which parameter is wrong"""
    if not parameter and getattr(exception, "_is_tip_exc", None):
        return exception
    if parameter:
        param_value: BaseField = parameter.default
        annotation: Type[BaseModel] = parameter.annotation
        param_name: str = parameter.name

        parameter_value_name: str = param_value.__class__.__name__
        if param_value is parameter.empty:
            param_str: str = f"{param_name}: {annotation}"
        else:
            param_str = f"{param_name}: {annotation} = {parameter_value_name}"
            if isinstance(param_value, BaseField):
                param_str += f"(alias={param_value.alias}, default={param_value.default})"
    else:
        param_str = ""

    file: Optional[str] = None
    if isinstance(_object, FuncSig):
        _object = _object.func
    if inspect.isfunction(_object):
        title: str = "def"
        if inspect.iscoroutinefunction(_object):
            title = "async def"
        file = inspect.getfile(_object)
        line: int = inspect.getsourcelines(_object)[1]
        error_object_name: str = _object.__name__
        logging.debug(
            f"""
{title} {error_object_name}(
    ...
    {param_str} <-- error
    ...
):
    pass
"""
        )
    else:
        module: Any = inspect.getmodule(_object)
        if module:
            file = module.__file__
        line = inspect.getsourcelines(_object.__class__)[1]
        error_object_name = _object.__class__.__name__
        if "class" in error_object_name:
            error_object_name = str(_object.__class__)
        logging.debug(f"class: `{error_object_name}`  attributes error\n    {param_str}")
    exc_msg: str = f'File "{file}",' f" line {line}," f" in {error_object_name}." f" error:{str(exception)}"
    try:
        exc: Exception = exception.__class__(exc_msg)
    except Exception:
        exc = PaitBaseException(exc_msg)
    setattr(exception, "_is_tip_exc", True)
    return exc
