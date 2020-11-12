import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Type, get_type_hints

from pydantic import BaseModel
from pait.field import BaseField
from pait.util import FuncSig


open_api_dict = {
    "openapi": "3.0.2",
    "info": {
        "title": "pait test open api",
        "description": "测试pait的openapi",
        "version": "0.1.0",
        "termsOfService": "",
        "contact": {
            "name": "Pait Api",
            "url": "http://www.example.support",
            "email": "pait@example.com"
        },
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        }
    },
    "servers": {
        "url": "/",
        "description": "test pait server"
    },
    "tags": {
        "name": "test",
        "description": "about test api",
        "externalDocs": {
            "description": "external docx",
            "url": " http://example.com"
        }
    },
    "paths": {

    },
    "components": {

    },
    "security": {

    },
    "externalDocs": {

    }
}

@dataclass()
class PaitInfoModel(object):
    func: Optional[Callable] = None
    func_name: Optional[str] = None
    method_set: Optional[Set[str]] = None
    path: Optional[str] = None
    pait_name: Optional[str] = None


class ParamModel(object):
    def __init__(self, func_sig: FuncSig, type_dict: Optional[Dict[type, str]] = None):

        self._parse_func_sig(func_sig)

    def _parse_annotation(self, annotation: type):
        pass

    def _parse_pydantic_model(self, pydantic_model: Type[BaseModel]):
        for param_name, param_annotation in get_type_hints(pydantic_model).items():
            field: BaseField = pydantic_model.__field_defaults__[param_name]
            bucket: Dict[str, Any] = getattr(self, field.__class__.__name__.lower())
            bucket[param_name] = self._parse_annotation(param_annotation)

    # def _parse_func_sig(self, func_sig: FuncSig):
    #     for cnt, parameter in enumerate(func_sig.param_list):
    #         if issubclass(parameter.annotation, PaitModel):
    #             _pait_model = parameter.annotation
    #             self._parse_pydantic_model(_pait_model)
    #         elif parameter.default != parameter.empty:
    #             bucket: Dict[str, Any] = getattr(self, parameter.default.__class__.__name__.lower())
    #             annotation: type = parameter.annotation
    #             if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
    #                 self._parse_pydantic_model(annotation)
    #             else:
    #                 bucket[parameter.name] = self._parse_annotation(annotation)


pait_name_dict: Dict[str, PaitInfoModel] = {}