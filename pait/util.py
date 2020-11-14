import inspect

from dataclasses import dataclass
from typing import Callable, List, Type, TYPE_CHECKING, Union, get_type_hints

from pydantic import BaseModel, create_model

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class PaitBaseModel(object):
    _pydantic_model: Type[BaseModel] = None

    @classmethod
    def to_pydantic_model(cls) -> Type[BaseModel]:
        if cls._pydantic_model:
            return cls._pydantic_model
        cls._pydantic_model: Type[BaseModel] = create_model('DynamicFoobarModel', **get_type_hints(cls))
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
        return self.to_pydantic_model(**self.__dict__).dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none
        )

    @classmethod
    def aaa(cls, by_alias: bool = True) -> 'DictStrAny':
        return cls.to_pydantic_model().schema(by_alias=by_alias)


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

