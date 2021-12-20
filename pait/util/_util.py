import inspect
import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type, get_type_hints

from pydantic import BaseConfig, BaseModel, create_model

from pait.exceptions import PaitBaseException
from pait.field import BaseField
from pait.g import config

from ._func_sig import FuncSig


class UndefinedType:
    def __repr__(self) -> str:
        return "PaitUndefined"


# pait undefined flag
Undefined: UndefinedType = UndefinedType()


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
        for key, value in obj.items():
            obj[key] = gen_example_json_from_python(value)
        return obj
    else:
        return config.python_type_default_value_dict.get(type(obj), obj)


def gen_example_dict_from_schema(
    schema_dict: Dict[str, Any], use_example_value: bool = False, definition_dict: Optional[dict] = None
) -> Dict[str, Any]:
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
                gen_dict[key] = [
                    gen_example_dict_from_schema(
                        _definition_dict.get(model_key, {}), use_example_value, _definition_dict
                    )
                ]
            else:
                gen_dict[key] = []
        elif "$ref" in value:
            model_key = value["$ref"].split("/")[-1]
            gen_dict[key] = gen_example_dict_from_schema(
                _definition_dict.get(model_key, {}), use_example_value, _definition_dict
            )
        else:
            if "example" in value:
                gen_dict[key] = value["example"]
                if inspect.isfunction(gen_dict[key]):
                    gen_dict[key] = gen_dict[key]()
            elif "default" in value:
                gen_dict[key] = value["default"]
            else:
                if "type" in value:
                    if value["type"] not in config.json_type_default_value_dict:
                        raise KeyError(f"Can not found type: {key} in json type")
                    gen_dict[key] = config.json_type_default_value_dict[value["type"]]
                else:
                    gen_dict[key] = "object()"
            if isinstance(gen_dict[key], Enum):
                gen_dict[key] = gen_dict[key].value
    return gen_dict


def gen_example_json_from_schema(schema_dict: Dict[str, Any], use_example_value: bool) -> str:
    return json.dumps(
        gen_example_dict_from_schema(schema_dict, use_example_value=use_example_value), cls=config.json_encoder
    )


def get_parameter_list_from_class(cbv_class: Type) -> List["inspect.Parameter"]:
    """get class parameter list by attributes, if attributes not default value, it will be set `Undefined`"""
    parameter_list: List["inspect.Parameter"] = getattr(cbv_class, "_parameter_list", [])
    if parameter_list:
        return parameter_list
    if hasattr(cbv_class, "__annotations__"):
        for param_name, param_annotation in get_type_hints(cbv_class).items():
            default: Any = getattr(cbv_class, param_name, Undefined)
            if not isinstance(default, BaseField):
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
    if getattr(exception, "_is_tip_exc", None):
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
