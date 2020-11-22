import inspect
from typing import Any, Dict, Optional, Type, get_type_hints

from pydantic import BaseModel
from pait.field import BaseField
from pait.model import FuncSig


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

    def _parse_func_sig(self, func_sig: FuncSig):
        for cnt, parameter in enumerate(func_sig.param_list):
            if parameter.default != parameter.empty:
                bucket: Dict[str, Any] = getattr(self, parameter.default.__class__.__name__.lower())
                annotation: type = parameter.annotation
                if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                    # def test(test_model: BaseModel = Body())
                    self._parse_pydantic_model(annotation)
                else:
                    # def test(test_model: int = Body())
                    bucket[parameter.name] = self._parse_annotation(annotation)
            if issubclass(parameter.annotation, BaseModel):
                # def test(test_model: BaseModel)
                _pait_model = parameter.annotation
                self._parse_pydantic_model(_pait_model)
