import inspect
import warnings
from types import CodeType
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, get_type_hints

from pydantic import BaseModel, create_model
from pydantic.fields import Undefined

from pait.field import BaseField, Depends
from pait.g import pait_data
from pait.model import FuncSig, PaitBaseModel, PaitCoreModel, PaitResponseModel
from pait.util import get_func_sig, get_parameter_list_from_class


class PaitBaseParse(object):
    def __init__(self, undefined: Any = Undefined):
        if not pait_data:
            raise RuntimeError(f"`pait info not init`, please run load_app")
        self._undefined: Any = undefined
        self._group_list: List[str] = []
        self._group_pait_dict: Dict[str, List[PaitCoreModel]] = {}

        self._init()

    def _init(self) -> None:
        """read from `pait_id_dict` and write PaitMd attributes"""
        for pait_id, pait_model in pait_data.pait_id_dict.items():
            group: str = pait_model.group
            if group not in self._group_pait_dict:
                self._group_pait_dict[group] = [pait_model]
            else:
                self._group_pait_dict[group].append(pait_model)
        self._group_list = sorted(self._group_pait_dict.keys())

    def _parse_schema(
        self, schema_dict: dict, definition_dict: Optional[dict] = None, parent_key: str = ""
    ) -> List[dict]:
        """gen field dict from pydantic basemodel schema"""
        field_dict_list: List[dict] = []
        property_dict: dict = schema_dict["properties"]
        if not definition_dict:
            definition_dict = schema_dict.get("definitions", {})
        for param_name, param_dict in property_dict.items():
            if parent_key:
                all_param_name: str = f"{parent_key}.{param_name}"
            else:
                all_param_name = param_name

            if "$ref" in param_dict and definition_dict:
                # ref support
                key: str = param_dict["$ref"].split("/")[-1]
                if isinstance(definition_dict, dict):
                    field_dict_list.extend(self._parse_schema(definition_dict[key], definition_dict, all_param_name))
            elif "items" in param_dict and "$ref" in param_dict["items"]:
                # mad item ref support
                key = param_dict["items"]["$ref"].split("/")[-1]
                if isinstance(definition_dict, dict):
                    field_dict_list.extend(self._parse_schema(definition_dict[key], definition_dict, all_param_name))
            else:
                if "enum" in param_dict:
                    # enum support
                    default: str = param_dict.get("enum", self._undefined)
                    if default is not self._undefined:
                        default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                    _type: str = "enum"
                else:
                    default = param_dict.get("default", self._undefined)
                    _type = param_dict["type"]
                field_dict_list.append(
                    {
                        "param_name": all_param_name,
                        "description": param_dict.get("description", ""),
                        "default": default,
                        "type": _type,
                        "other": {
                            key: value
                            for key, value in param_dict.items()
                            if key not in {"description", "title", "type", "default"}
                        },
                        "raw": {
                            "param_name": param_name,
                            "schema": param_dict,
                            "parent_schema": schema_dict,
                        },
                    }
                )
        return field_dict_list

    def _parse_base_model(
        self,
        field_dict: Dict[str, List[Dict[str, Any]]],
        _pydantic_model: Type[BaseModel],
        _pait_field_dict: Dict[str, BaseField],
    ) -> None:
        """gen field dict"""
        # TODO design like _parse_schema
        param_python_name_dict: Dict[str, str] = {
            value.alias: key for key, value in _pait_field_dict.items() if value.alias
        }
        property_dict: Dict[str, Any] = _pydantic_model.schema()["properties"]
        for param_name, param_dict in property_dict.items():
            param_python_name: str = param_python_name_dict.get(param_name, param_name)
            field_name = _pait_field_dict[param_python_name].__class__.__name__.lower()
            if "$ref" in param_dict:
                # ref support
                key: str = param_dict["$ref"].split("/")[-1]
                param_dict = _pydantic_model.schema()["definitions"][key]
            elif "items" in param_dict and "$ref" in param_dict["items"]:
                # mad item ref support
                key = param_dict["items"]["$ref"].split("/")[-1]
                param_dict = _pydantic_model.schema()["definitions"][key]
            elif "allOf" in param_dict:
                if len(param_dict["allOf"]) > 1:
                    warnings.warn(f"{param_dict['param_name']} only support 1 item")

                param_dict.update(param_dict["allOf"][0])
                key = param_dict["$ref"].split("/")[-1]
                param_dict = _pydantic_model.schema()["definitions"][key]
            if "enum" in param_dict:
                # enum support
                default: str = param_dict.get("enum", self._undefined)
                if default is not self._undefined:
                    default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                _type: str = "enum"
                description: str = _pait_field_dict[param_python_name].description
            else:
                default = param_dict.get("default", self._undefined)
                _type = param_dict["type"]
                description = param_dict.get("description")
            _field_dict = {
                "param_name": param_name,
                "description": description,
                "default": default,
                "type": _type,
                "other": {
                    key: value
                    for key, value in param_dict.items()
                    if key not in {"description", "title", "type", "default"}
                },
                "raw": {
                    "param_name": param_name,
                    "schema": param_dict,
                    "parent_schema": _pydantic_model.schema(),
                    "annotation": _pydantic_model.__annotations__[param_python_name],
                    "field": _pait_field_dict[param_python_name],
                },
            }
            if field_name not in field_dict:
                field_dict[field_name] = [_field_dict]
            else:
                field_dict[field_name].append(_field_dict)

    def parameter_list_handle(
        self,
        parameter_list: List["inspect.Parameter"],
        field_dict: Dict[str, List[Dict[str, Any]]],
        single_field_list: List[Tuple[str, "inspect.Parameter"]],
    ) -> None:
        """gen field dict from parameter_list"""
        for parameter in parameter_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    _pait_field_dict: Dict[str, BaseField] = {
                        param_name: parameter.default
                        for param_name, annotation in get_type_hints(annotation).items()
                        if not param_name.startswith("_")
                    }
                    self._parse_base_model(field_dict, annotation, _pait_field_dict)
                else:
                    # def test(test_model: int = Body())
                    if isinstance(parameter.default, Depends):
                        field_dict.update(self._parse_func_param(parameter.default.func))
                    else:
                        field_name: str = parameter.default.__class__.__name__.lower()
                        single_field_list.append((field_name, parameter))
            elif issubclass(parameter.annotation, PaitBaseModel):
                # def test(test_model: PaitBaseModel)
                _pait_model: Type[PaitBaseModel] = parameter.annotation
                _pait_field_dict = {}
                for param_name, param_annotation in get_type_hints(_pait_model).items():
                    if param_name.startswith("_"):
                        continue
                    field: BaseField = getattr(_pait_model, param_name)
                    _pait_field_dict[param_name] = field

                pait_base_model = _pait_model.to_pydantic_model()
                self._parse_base_model(field_dict, pait_base_model, _pait_field_dict)

    def _parse_func_param(self, func: Callable) -> Dict[str, List[Dict[str, Any]]]:
        """gen filed dict from func
        [
            {
                'field': {
                    'param_name': str,
                    'description': str,
                    'default': str,
                    'type': type,
                    'other': dict,
                    'raw': {
                        'param_name': str,
                        'schema': dict,
                        'parent_schema': pydantic base model.schema(),
                        'annotation': annotation,
                        'field': basefield,
                    }
                }
            }
        ]
        """
        field_dict: Dict[str, List[Dict[str, Any]]] = {}
        func_sig: FuncSig = get_func_sig(func)
        single_field_list: List[Tuple[str, "inspect.Parameter"]] = []

        qualname = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
        class_ = getattr(inspect.getmodule(func), qualname)
        if inspect.isclass(class_):
            parameter_list: List["inspect.Parameter"] = get_parameter_list_from_class(class_)
            self.parameter_list_handle(parameter_list, field_dict, single_field_list)
        self.parameter_list_handle(func_sig.param_list, field_dict, single_field_list)

        if single_field_list:
            annotation_dict: Dict[str, Tuple] = {}
            _pait_field_dict: Dict[str, BaseField] = {}
            for field_name, parameter in single_field_list:
                field: BaseField = parameter.default
                annotation_dict[parameter.name] = (parameter.annotation, field)
                _pait_field_dict[parameter.name] = field

            _pydantic_model: Type[BaseModel] = create_model("DynamicFoobarModel", **annotation_dict)
            self._parse_base_model(field_dict, _pydantic_model, _pait_field_dict)
        return field_dict

    def gen_dict(self) -> Dict[str, Any]:
        api_doc_dict: Dict[str, Any] = {"group": {}}
        for group in self._group_list:
            group_dict: Dict[str, Any] = {"name": group, "group_list": []}
            api_doc_dict["group"][group] = group_dict
            for pait_model in self._group_pait_dict[group]:
                func_code: CodeType = pait_model.func.__code__
                response_list: List[Dict[str, Any]] = []
                if pait_model.response_model_list:
                    for resp_model_class in pait_model.response_model_list:
                        resp_model: PaitResponseModel = resp_model_class()
                        if resp_model.response_data:
                            schema_dict: dict = resp_model.response_data.schema()
                        else:
                            schema_dict = {}
                        response_list.append(
                            {
                                "status_code": ",".join([str(i) for i in resp_model.status_code]),
                                "media_type": resp_model.media_type,
                                "description": resp_model.description,
                                "header": resp_model.header,
                                "response_data": self._parse_schema(schema_dict),
                            }
                        )
                field_dict: Dict[str, List[Dict[str, Any]]] = self._parse_func_param(pait_model.func)
                for field_name, field_dict_list in field_dict.items():
                    for field_dict in field_dict_list:
                        del field_dict["raw"]

                group_dict["group_list"].append(
                    {
                        "name": pait_model.operation_id,
                        "status": pait_model.status.value,
                        "author": ",".join(pait_model.author),
                        "func": {
                            "file": func_code.co_filename,
                            "lineno": func_code.co_firstlineno,
                            "name": pait_model.func.__qualname__,
                        },
                        "path": pait_model.path,
                        "method": list(pait_model.method_set),
                        "request": field_dict,
                        "response_list": response_list,
                    }
                )
        return api_doc_dict

    @staticmethod
    def output(filename: Optional[str], content: str, suffix: str) -> None:
        if not filename:
            print(content)
        else:
            if not filename.endswith(suffix):
                filename += suffix
            with open(filename, mode="w") as f:
                f.write(content)
