import inspect
from typing import Any, Callable, Dict, List, Tuple, Type, get_type_hints
from types import CodeType

from pydantic import create_model, BaseModel
from pydantic.fields import Undefined
from pait.g import pait_data
from pait.data import PaitInfoModel
from pait.field import BaseField, Depends
from pait.util import FuncSig, PaitBaseModel, get_func_sig


class PaitMd(object):
    def __init__(self, title: str = 'Pait Doc', use_html_details: bool = True):
        if not pait_data:
            raise RuntimeError(f'`pait info not init`, please run load_app')
        self._use_html_details: bool = use_html_details  # some not support markdown in html
        self._title: str = title
        self._tag_list: List[str] = []
        self._tag_pait_dict: Dict[str, List[PaitInfoModel]] = {}

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

    def gen_markdown_text(self):
        markdown_text: str = f"# {self._title}\n"
        for tag in self._tag_list:
            # tag
            if self._use_html_details:
                markdown_text += f"<details><summary>Tag: {tag}</summary>\n"
            else:
                markdown_text += f"## Tag: {tag}\n"
            for pait_model in self._tag_pait_dict[tag]:
                # func info
                markdown_text += f"### Name: {pait_model.operation_id}\n"
                func_code: CodeType = pait_model.func.__code__
                markdown_text += f"- Func: {pait_model.func.__qualname__};" \
                                 f" file:{func_code.co_filename};" \
                                 f" line: {func_code.co_firstlineno}\n"

                # request info
                markdown_text += f"- Path: {pait_model.path}\n"
                markdown_text += f"- Method: {','.join(pait_model.method_set)}\n"
                markdown_text += f"- Request:\n"

                field_dict = self._parse_func(pait_model.func)
                field_key_list = sorted(field_dict.keys())
                # request body info
                for field in field_key_list:
                    field_dict_list = field_dict[field]
                    markdown_text += f"{' ' * 4}- {field.capitalize()}\n"
                    markdown_text += f"{' ' * 8}|param name|type|default value|description|other|\n"
                    markdown_text += f"{' ' * 8}|---|---|---|---|---|\n"
                    for field_info_dict in field_dict_list:
                        default = field_info_dict['default']
                        if default is Undefined:
                            default = '**`Required`**'
                        description = field_info_dict['description']
                        other_dict = field_info_dict.get('other', None)
                        if other_dict:
                            other_dict = {
                                key: value
                                for key, value in other_dict.items()
                                if key not in {'description', 'title', 'type', 'default'}
                            }
                        markdown_text += f"{' ' * 8}|{field_info_dict['param_name']}" \
                                         f"|{field_info_dict['type']}" \
                                         f"|{default}" \
                                         f"|{description}" \
                                         f"|{other_dict}"\
                                         f"|\n"
                # response info
                markdown_text += f"- Response:\n"
                markdown_text += "\n"
            if self._use_html_details:
                markdown_text += "</details>"
        print(markdown_text)

    @staticmethod
    def _parse_base_model(
        field_dict: Dict[str, List[Dict[str, Any]]],
        _pydantic_model: Type[BaseModel],
        _pait_field_dict: Dict[str, BaseField]
    ):
        property_dict: Dict[str, Any] = _pydantic_model.schema()['properties']
        for param_name, param_dict in property_dict.items():
            field_name = _pait_field_dict[param_name].__class__.__name__.lower()
            if '$ref' in param_dict:
                # ref support
                key: str = param_dict['$ref'].split('/')[-1]
                param_dict: Dict[str, Any] = _pydantic_model.schema()['definitions'][key]
            if 'enum' in param_dict:
                # enum support
                default: str = param_dict.get('enum')
                if not default:
                    default = Undefined
                else:
                    default = f'Only choose from: {",".join(["`" + i + "`" for i in default])}'
                _type: str = 'enum'
                description: str = _pait_field_dict[param_name].description
            else:
                default = param_dict.get('default', Undefined)
                _type = param_dict['type']
                description = param_dict.get('description')
                param_name = param_dict['title']
            _field_dict = {
                'param_name': param_name,
                'description': description,
                'default': default,
                'type': _type,
                'other': param_dict
            }
            if field_name not in field_dict:
                field_dict[field_name] = [_field_dict]
            else:
                field_dict[field_name].append(_field_dict)

    def _parse_func(self, func: Callable) -> Dict[str, List[Dict[str, Any]]]:
        field_dict: Dict[str, List[Dict[str, Any]]] = {}
        func_sig: FuncSig = get_func_sig(func)
        single_field_dict = {}
        for parameter in func_sig.param_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                field_name: str = parameter.default.__class__.__name__.lower()
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    property_dict: Dict[str, Dict[str, Any]] = annotation.schema()['properties']
                    for param_name, param_dict in property_dict.items():
                        _field_dict = {
                            'param_name': param_dict['title'],
                            'description': param_dict['description'],
                            'default': param_dict.get('default', Undefined),
                            'type': param_dict['type'],
                            'other': param_dict
                        }
                        if field_name not in field_dict:
                            field_dict[field_name] = [_field_dict]
                        else:
                            field_dict[field_name].append(_field_dict)
                else:
                    # def test(test_model: int = Body())
                    if isinstance(parameter.default, Depends):
                        field_dict.update(self._parse_func(parameter.default.func))
                    else:
                        single_field_dict[field_name] = parameter
            elif issubclass(parameter.annotation, PaitBaseModel):
                # def test(test_model: PaitBaseModel)
                _pait_model: Type[PaitBaseModel] = parameter.annotation
                _pait_field_dict = {
                    param_name: getattr(_pait_model, param_name)
                    for param_name, param_annotation in get_type_hints(_pait_model).items()
                    if not param_name.startswith('_')
                }
                pait_base_model = _pait_model.to_pydantic_model()
                self._parse_base_model(field_dict, pait_base_model, _pait_field_dict)

        if single_field_dict:
            annotation_dict: Dict[str, Tuple] = {}
            _pait_field_dict: Dict[str, BaseField] = {}
            for field, parameter in single_field_dict.items():
                annotation_dict[parameter.name] = (parameter.annotation, parameter.default)
                _pait_field_dict[parameter.name] = parameter.default

            _pydantic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **annotation_dict)
            self._parse_base_model(field_dict, _pydantic_model, _pait_field_dict)
        return field_dict
