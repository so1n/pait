import inspect

from dataclasses import InitVar, dataclass, field
from typing import Callable, Dict, List, Optional, Type, TYPE_CHECKING, Union, get_type_hints

from pydantic import BaseModel, create_model

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


@dataclass()
class PaitResponseModel(object):
    description: Optional[str] = ''
    header: dict = field(default_factory=dict)
    media_type: str = "application/json"
    response_data: Optional[BaseModel] = None
    status_code: List[int] = field(default_factory=lambda: [200])

    name: InitVar[str] = None

    def __post_init__(self, name: InitVar[str]):
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__


class PaitBaseModel(object):
    _pydantic_model: Type[BaseModel] = None

    @classmethod
    def to_pydantic_model(cls) -> Type[BaseModel]:
        if cls._pydantic_model:
            return cls._pydantic_model
        annotation_dict: Dict[str, Type] = {
            param_name: (annotation, getattr(cls, param_name, ...))
            for param_name, annotation in get_type_hints(cls).items()
            if not param_name.startswith('_')
        }
        cls._pydantic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **annotation_dict)
        return cls._pydantic_model

    def dict(
        self,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> 'DictStrAny':
        _pydantic_model: BaseModel = self._pydantic_model()(**self.__dict__)
        return _pydantic_model.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none
        )

    @classmethod
    def schema(cls, by_alias: bool = True) -> 'DictStrAny':
        return cls.to_pydantic_model().schema(by_alias=by_alias)


class UndefinedType:
    def __repr__(self) -> str:
        return 'PaitUndefined'


Undefined: UndefinedType = UndefinedType()


@dataclass()
class FuncSig:
    func: Callable
    sig: 'inspect.Signature'
    param_list: List['inspect.Parameter']


def get_func_sig(func: Callable) -> FuncSig:
    sig: 'inspect.signature' = inspect.signature(func)
    param_list: List[inspect.Parameter] = [
        sig.parameters[key]
        for key in sig.parameters
        if sig.parameters[key].annotation != sig.empty or sig.parameters[key].name == 'self'
    ]
    # return_param = sig.return_annotation
    return FuncSig(func=func, sig=sig, param_list=param_list)


def get_parameter_list_from_class(cbv_class: Type) -> List['inspect.Parameter']:
    parameter_list: List['inspect.Parameter'] = []
    if not hasattr(cbv_class, '__annotations__'):
        return parameter_list
    for param_name, param_annotation in get_type_hints(cbv_class).items():
        parameter: 'inspect.Parameter' = inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=getattr(cbv_class, param_name),
            annotation=param_annotation)
        parameter_list.append(parameter)
    return parameter_list