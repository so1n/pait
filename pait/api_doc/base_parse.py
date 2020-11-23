import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, get_type_hints

from pydantic import create_model, BaseModel
from pydantic.fields import Undefined
from pait.g import pait_data
from pait.model import PaitCoreModel, PaitBaseModel, FuncSig
from pait.field import BaseField, Depends
from pait.util import get_func_sig, get_parameter_list_from_class


class PaitBaseParse(object):
    def __init__(self):
        if not pait_data:
            raise RuntimeError(f'`pait info not init`, please run load_app')
        self._tag_list: List[str] = []
        self._tag_pait_dict: Dict[str, List[PaitCoreModel]] = {}

        self._init()

    def _init(self):
        """read from `pait_id_dict` and write PaitMd attributes"""
        for pait_id, pait_model in pait_data.pait_id_dict.items():
            tag: str = pait_model.tag
            if tag not in self._tag_pait_dict:
                self._tag_pait_dict[tag] = [pait_model]
            else:
                self._tag_pait_dict[tag].append(pait_model)
        self._tag_list = sorted(self._tag_pait_dict.keys())

    def _parse_schema(
            self, schema_dict: dict, definition_dict: Optional[dict] = None, parent_key: str = ''
    ) -> List[dict]:
        field_dict_list: List[dict] = []
        property_dict: dict = schema_dict['properties']
        if not definition_dict:
            definition_dict = schema_dict.get('definitions', {})
        for param_name, param_dict in property_dict.items():
            if parent_key:
                all_param_name: str = f'{parent_key}.{param_name}'
            else:
                all_param_name = param_name

            if '$ref' in param_dict and definition_dict:
                # ref support
                key: str = param_dict['$ref'].split('/')[-1]
                field_dict_list.extend(self._parse_schema(definition_dict[key], definition_dict, all_param_name))
            elif 'items' in param_dict and '$ref' in param_dict['items']:
                # mad item ref support
                key: str = param_dict['items']['$ref'].split('/')[-1]
                field_dict_list.extend(self._parse_schema(definition_dict[key], definition_dict, all_param_name))
            else:
                if 'enum' in param_dict:
                    # enum support
                    default: str = param_dict.get('enum', Undefined)
                    if default is not Undefined:
                        default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                    _type: str = 'enum'
                else:
                    default = param_dict.get('default', Undefined)
                    _type = param_dict['type']
                field_dict_list.append({
                    'param_name': all_param_name,
                    'description': param_dict.get('description', ''),
                    'default': default,
                    'type': _type,
                    'other': {
                        key: value
                        for key, value in param_dict.items()
                        if key not in {'description', 'title', 'type', 'default'}
                    }
                })
        return field_dict_list

    @staticmethod
    def _parse_base_model(
        field_dict: Dict[str, List[Dict[str, Any]]],
        _pydantic_model: Type[BaseModel],
        _pait_field_dict: Dict[str, BaseField]
    ):
        # TODO design like _parse_schema
        property_dict: Dict[str, Any] = _pydantic_model.schema()['properties']
        for param_name, param_dict in property_dict.items():
            field_name = _pait_field_dict[param_name].__class__.__name__.lower()
            if '$ref' in param_dict:
                # ref support
                key: str = param_dict['$ref'].split('/')[-1]
                param_dict: Dict[str, Any] = _pydantic_model.schema()['definitions'][key]
            elif 'items' in param_dict and '$ref' in param_dict['items']:
                # mad item ref support
                key: str = param_dict['items']['$ref'].split('/')[-1]
                param_dict: Dict[str, Any] = _pydantic_model.schema()['definitions'][key]
            if 'enum' in param_dict:
                # enum support
                default: str = param_dict.get('enum', Undefined)
                if default is not Undefined:
                    default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                _type: str = 'enum'
                description: str = _pait_field_dict[param_name].description
            else:
                default = param_dict.get('default', Undefined)
                _type = param_dict['type']
                description = param_dict.get('description')
            _field_dict = {
                'param_name': param_name,
                'description': description,
                'default': default,
                'type': _type,
                'other': {
                    key: value
                    for key, value in param_dict.items()
                    if key not in {'description', 'title', 'type', 'default'}
                }
            }
            if field_name not in field_dict:
                field_dict[field_name] = [_field_dict]
            else:
                field_dict[field_name].append(_field_dict)

    def parameter_list_handle(
        self,
        parameter_list: List['inspect.Parameter'],
        field_dict: Dict[str, List[Dict[str, Any]]],
        single_field_dict: Dict[str, 'inspect.Parameter']
    ):
        for parameter in parameter_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    _pait_field_dict = {
                        param_name: parameter.default
                        for param_name, annotation in get_type_hints(annotation).items()
                        if not param_name.startswith('_')
                    }
                    self._parse_base_model(field_dict, annotation, _pait_field_dict)
                else:
                    # def test(test_model: int = Body())
                    if isinstance(parameter.default, Depends):
                        field_dict.update(self._parse_func_param(parameter.default.func))
                    else:
                        field_name: str = parameter.default.__class__.__name__.lower()
                        single_field_dict[field_name] = parameter
            elif issubclass(parameter.annotation, PaitBaseModel):
                # def test(test_model: PaitBaseModel)
                _pait_model: Type[PaitBaseModel] = parameter.annotation
                _pait_field_dict: Dict[str, BaseField] = {}
                for param_name, param_annotation in get_type_hints(_pait_model).items():
                    if param_name.startswith('_'):
                       continue
                    field: BaseField = getattr(_pait_model, param_name)
                    key: str = field.alias if field.alias else param_name
                    _pait_field_dict[key] = field

                pait_base_model = _pait_model.to_pydantic_model()
                self._parse_base_model(field_dict, pait_base_model, _pait_field_dict)

    def _parse_func_param(self, func: Callable) -> Dict[str, List[Dict[str, Any]]]:
        field_dict: Dict[str, List[Dict[str, Any]]] = {}
        func_sig: FuncSig = get_func_sig(func)
        single_field_dict: Dict[str, 'inspect.Parameter'] = {}

        qualname = func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
        class_ = getattr(inspect.getmodule(func), qualname)
        if inspect.isclass(class_):
            parameter_list: List['inspect.Parameter'] = get_parameter_list_from_class(class_)
            self.parameter_list_handle(parameter_list, field_dict, single_field_dict)
        self.parameter_list_handle(func_sig.param_list, field_dict, single_field_dict)

        if single_field_dict:
            annotation_dict: Dict[str, Tuple] = {}
            _pait_field_dict: Dict[str, BaseField] = {}
            for field_name, parameter in single_field_dict.items():
                field: BaseField = parameter.default
                annotation_dict[parameter.name] = (parameter.annotation, field)
                key: str = field.alias if field.alias else parameter.name
                _pait_field_dict[key] = field

            _pydantic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **annotation_dict)
            self._parse_base_model(field_dict, _pydantic_model, _pait_field_dict)

        return field_dict
