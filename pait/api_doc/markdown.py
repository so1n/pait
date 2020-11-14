import inspect
from typing import Any, Callable, Dict, List, get_type_hints
from types import CodeType

from pydantic import BaseModel
from pait.g import pait_id_dict, PaitInfoModel
from pait.field import BaseField, Depends, FactoryField
from pait.util import FuncSig, get_func_sig


class PaitMd(object):
    def __init__(self, title: str = 'Pait Doc', use_html_details: bool = True):
        self._use_html_details: bool = use_html_details  # some not support markdown in html
        self._title: str = title
        self._tag_list: List[str] = []
        self._tag_pait_dict: Dict[str, List[PaitInfoModel]] = {}

        self._init()

    def _init(self):
        for pait_id, pait_model in pait_id_dict.items():
            tag: str = pait_model.tag
            if tag not in self._tag_pait_dict:
                self._tag_pait_dict[tag] = [pait_model]
            else:
                self._tag_pait_dict[tag].append(pait_model)

        self._tag_list = sorted(self._tag_pait_dict.keys())

    def gen_markdown_text(self):
        markdown_text: str = f"# {self._title}\n"
        for tag in self._tag_list:
            if self._use_html_details:
                markdown_text += f"<details><summary>Tag:{tag}</summary>\n"
            else:
                markdown_text += "## Tag:{tag}\n"
            for pait_model in self._tag_pait_dict[tag]:
                markdown_text += f"### Name:{pait_model.operation_id}\n"
                func_code: CodeType = pait_model.func.__code__
                markdown_text += f"- Func:{pait_model.func.__qualname__};" \
                                 f" file:{func_code.co_filename};" \
                                 f" line: {func_code.co_firstlineno}\n"

                markdown_text += f"- Path:{pait_model.path}\n"
                markdown_text += f"- Method:{','.join(pait_model.method_set)}\n"
                markdown_text += f"- Request:\n"
                field_dict = self._parse_func(pait_model.func)
                field_list = sorted(field_dict.keys())
                for field in field_list:
                    field_dict_list = field_dict[field]
                    markdown_text += f"    - {field.capitalize()}\n"
                    markdown_text += f"        |param name|type|description|example|\n"
                    markdown_text += f"        |---|---|---|---|\n"
                    for sub_field_dict in field_dict_list:
                        annotation_name = getattr(
                            sub_field_dict['annotation'],
                            '__name__',
                            str(sub_field_dict['annotation'])
                        )
                        markdown_text += f"        |{sub_field_dict['param_name']}|{annotation_name}|||\n"
                markdown_text += f"- Response:\n"
                markdown_text += "\n"
            if self._use_html_details:
                markdown_text += "</details>"
        print(markdown_text)

    def _parse_func(self, func: Callable) -> Dict[str, List[Dict[str, Any]]]:
        field_dict: Dict[str, List[Dict[str, Any]]] = {}
        func_sig: FuncSig = get_func_sig(func)
        for parameter in func_sig.param_list:
            if parameter.default != parameter.empty:
                annotation: type = parameter.annotation
                field_name: str = parameter.default.__class__.__name__.lower()
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    for base_model_name, base_model_annotation in get_type_hints(annotation).items():
                        _field_dict = {
                            'annotation': base_model_annotation,
                            'field': parameter.default,
                            'name': field_name,
                            'param_name': base_model_name
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
                        param_name = getattr(parameter.default, 'key', None)
                        if not param_name:
                            param_name = parameter.name
                        _field_dict = {
                            'annotation': annotation,
                            'field': parameter.default,
                            'name': field_name,
                            'param_name': param_name
                        }
                        if field_name not in field_dict:
                            field_dict[field_name] = [_field_dict]
                        else:
                            field_dict[field_name].append(_field_dict)
            elif issubclass(parameter.annotation, BaseModel):
                # def test(test_model: BaseModel)
                _pait_model = parameter.annotation
                for param_name, param_annotation in get_type_hints(_pait_model).items():
                    field: BaseField = _pait_model.__field_defaults__[param_name]
                    if isinstance(field, FactoryField):
                        field: BaseField = field.field
                        field_name: str = field.__class__.__name__.lower()
                        _field_dict = {
                            'annotation': param_annotation,
                            'field': field,
                            'name': field_name,
                            'param_name': param_name
                        }
                        if field_name not in field_dict:
                            field_dict[field_name] = [_field_dict]
                        else:
                            field_dict[field_name].append(_field_dict)
        return field_dict
