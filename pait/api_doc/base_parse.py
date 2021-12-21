import inspect
import warnings
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, get_type_hints

from pydantic import BaseModel
from pydantic.fields import Undefined
from typing_extensions import TypedDict

from pait.field import BaseField, Depends
from pait.model.base_model import PaitBaseModel
from pait.model.core import PaitCoreModel
from pait.util import FuncSig, create_pydantic_model, get_func_sig, get_parameter_list_from_class


class _IgnoreField(BaseField):
    pass


class FieldSchemaRawTypeDict(TypedDict):
    param_name: str
    schema: dict
    parent_schema: dict
    annotation: Type
    field: BaseField


class FieldSchemaTypeDict(TypedDict):
    param_name: str
    description: str
    default: Any
    type: str
    other: dict
    raw: FieldSchemaRawTypeDict


FieldDictType = Dict[Type[BaseField], List[FieldSchemaTypeDict]]


class PaitBaseParse(object):
    def __init__(self, pait_dict: Dict[str, PaitCoreModel], undefined: Any = Undefined):
        self._undefined: Any = undefined
        self._group_list: List[str] = []
        self._group_pait_dict: Dict[str, List[PaitCoreModel]] = {}

        self._init(pait_dict)
        self.content: str = ""
        self._content_type: str = ""

    def _init(self, pait_dict: Dict[str, PaitCoreModel]) -> None:
        """read from `pait_id_dict` and write PaitMd attributes"""
        for pait_id, pait_model in pait_dict.items():
            if not pait_model.operation_id:
                continue
            group: str = pait_model.group
            if group not in self._group_pait_dict:
                self._group_pait_dict[group] = [pait_model]
            else:
                self._group_pait_dict[group].append(pait_model)
        self._group_list = sorted(self._group_pait_dict.keys())

    def _parse_schema(
        self, schema_dict: dict, definition_dict: Optional[dict] = None, parent_key: str = ""
    ) -> List[FieldSchemaTypeDict]:
        """gen pait field dict from pydantic basemodel schema"""
        field_dict_list: List[FieldSchemaTypeDict] = []
        # model property openapi dict
        # e.g. : {'code': {'title': 'Code', 'description': 'api code', 'default': 1, 'type': 'integer'}}
        property_dict: dict = schema_dict["properties"]
        # class schema in the parent schema
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
            elif "allOf" in param_dict:
                for item in param_dict["allOf"]:
                    key = item["$ref"].split("/")[-1]
                    if not isinstance(definition_dict, dict):
                        continue
                    if "enum" in definition_dict[key]:
                        if len(param_dict["allOf"]) > 1:
                            raise RuntimeError("Not support")
                        default: Any = definition_dict[key].get("enum", self._undefined)
                        if default is not self._undefined:
                            default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                        _type: str = "enum"
            else:
                if "enum" in param_dict:
                    # enum support
                    default = param_dict.get("enum", self._undefined)
                    if default is not self._undefined:
                        default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                    _type = "enum"
                else:
                    default = param_dict.get("default", self._undefined)
                    _type = param_dict.get("type", "object()")

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
                            # can not parse annotation and field
                            "annotation": str,
                            "field": _IgnoreField.i(),
                        },
                    }
                )
        return field_dict_list

    def _parse_base_model_to_field_dict(
        self,
        field_dict: FieldDictType,
        _pydantic_model: Type[BaseModel],
        param_field_dict: Dict[str, BaseField],
    ) -> None:
        """
        write field_dict from _pydantic_model or param_field_dict
        :param field_dict:
          e.g.
            {
                "Body": [
                    {
                        "param_name": "",
                        "description": "",
                        "default": "",
                        "type": _"",
                        "other": {"": ""},
                        "raw": {
                            "param_name": "",
                            "schema": {"": ""},
                            "parent_schema": {"": ""},
                        },
                    }
                ]
            }
        :param _pydantic_model: pydantic.basemodel
        :param param_field_dict:
            e.g.
            {
                'uid': Query(default=Ellipsis, description='user id', gt=10, lt=1000, extra={}),
                'user_name': Query(default=Ellipsis, description='user name', min_length=2, max_length=4, extra={}),
                'user_agent': Header(
                    default=Ellipsis, alias='user-agent', alias_priority=2, description='user agent', extra={}
                ),
                'age': Body(default=Ellipsis, description='age', gt=1, lt=100, extra={})
            }
        :return:
        """
        # TODO design like _parse_schema
        param_name_alias_dict: Dict[str, str] = {
            value.alias: key for key, value in param_field_dict.items() if isinstance(value, BaseField) and value.alias
        }
        property_dict: Dict[str, Any] = _pydantic_model.schema()["properties"]
        for param_name, param_dict in property_dict.items():
            param_python_name: str = param_name_alias_dict.get(param_name, param_name)
            pait_field: BaseField = param_field_dict[param_python_name]
            pait_field_class: Type[BaseField] = pait_field.__class__
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
                default: Any = param_dict.get("enum", self._undefined)
                if default is not self._undefined:
                    default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                _type: str = "enum"
                description: str = param_field_dict[param_python_name].description
            else:
                default = param_dict.get("default", self._undefined)
                _type = param_dict.get("type", self._undefined)
                description = param_dict.get("description")
            # NOTE: I do not know <pydandic.Filed(default=None)> can not found default value
            if default is self._undefined and param_name not in _pydantic_model.schema().get("required", []):
                default = param_field_dict[param_python_name].default
            _field_dict: FieldSchemaTypeDict = {
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
                    "field": pait_field,
                },
            }
            if pait_field_class not in field_dict:
                field_dict[pait_field_class] = [_field_dict]
            else:
                field_dict[pait_field_class].append(_field_dict)

    def parameter_list_handle(
        self,
        parameter_list: List["inspect.Parameter"],
        field_dict: FieldDictType,
        single_field_list: List[Tuple[str, "inspect.Parameter"]],
    ) -> None:
        """parse parameter_list to field_dict and single_field_list"""
        for parameter in parameter_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    param_filed_dict: Dict[str, BaseField] = {
                        param_name: parameter.default
                        for param_name, _ in get_type_hints(annotation).items()
                        # if not param_name.startswith("_")
                    }
                    self._parse_base_model_to_field_dict(field_dict, annotation, param_filed_dict)
                else:
                    # def test(test_model: int = Body())
                    if isinstance(parameter.default, Depends):
                        field_dict.update(self._parse_func_param_to_field_dict(parameter.default.func))
                    else:
                        field_name: str = parameter.default.__class__.__name__.lower()
                        single_field_list.append((field_name, parameter))
            elif issubclass(parameter.annotation, PaitBaseModel):
                # def test(test_model: PaitBaseModel)
                _pait_model: Type[PaitBaseModel] = parameter.annotation
                param_filed_dict = {
                    param_name: getattr(_pait_model, param_name)
                    for param_name, _ in get_type_hints(_pait_model).items()
                    # if not param_name.startswith("_")
                }
                pait_base_model = _pait_model.to_pydantic_model()
                self._parse_base_model_to_field_dict(field_dict, pait_base_model, param_filed_dict)

    def _parse_func_param_to_field_dict(self, func: Callable) -> FieldDictType:
        """gen filed dict from func
        {
            "Body": [
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
        }
        """
        field_dict: FieldDictType = {}
        func_sig: FuncSig = get_func_sig(func)
        single_field_list: List[Tuple[str, "inspect.Parameter"]] = []

        qualname = func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
        class_ = getattr(inspect.getmodule(func), qualname)
        if inspect.isclass(class_):
            parameter_list: List["inspect.Parameter"] = get_parameter_list_from_class(class_)
            self.parameter_list_handle(parameter_list, field_dict, single_field_list)
        self.parameter_list_handle(func_sig.param_list, field_dict, single_field_list)

        if single_field_list:
            annotation_dict: Dict[str, Tuple[Type, Any]] = {}
            _pait_field_dict: Dict[str, BaseField] = {}
            _column_name_set: Set[str] = set()
            for field_name, parameter in single_field_list:
                field: BaseField = parameter.default
                key: str = field.alias or parameter.name
                if key in _column_name_set:
                    # Since the same name cannot exist together in a Dict,
                    #  it will be parsed directly when a Key exists
                    # fix
                    #  class Demo(BaseModel):
                    #      header_token: str = Header(alias="token")
                    #      query_token: str = Query(alias="token")
                    _pydantic_model: Type[BaseModel] = create_pydantic_model(
                        {parameter.name: (parameter.annotation, field)}
                    )
                    self._parse_base_model_to_field_dict(field_dict, _pydantic_model, {parameter.name: field})
                else:
                    _column_name_set.add(key)
                    annotation_dict[parameter.name] = (parameter.annotation, field)
                    _pait_field_dict[parameter.name] = field

            _pydantic_model = create_pydantic_model(annotation_dict)
            self._parse_base_model_to_field_dict(field_dict, _pydantic_model, _pait_field_dict)
        return field_dict

    def output(self, filename: Optional[str], suffix: str = "") -> None:
        if not suffix:
            suffix = self._content_type
        if not filename:
            print(self.content)
        else:
            if not filename.endswith(suffix):
                filename += suffix
            with open(filename, mode="w") as f:
                f.write(self.content)
