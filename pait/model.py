from dataclasses import dataclass, field, InitVar
from enum import Enum
from typing import Callable, Dict, Optional, Set, Tuple, List, Type, TYPE_CHECKING, Union, get_type_hints

from pydantic import BaseModel, create_model

if TYPE_CHECKING:
    import inspect
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class PaitStatus(Enum):
    dev: 'PaitStatus' = 'dev'
    test: 'PaitStatus' = 'test'
    release: 'PaitStatus' = 'release'
    archive: 'PaitStatus' = 'archive'
    abandoned: 'PaitStatus' = 'abandoned'


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


@dataclass()
class PaitCoreModel(object):
    func: Callable                           # func object
    func_name: str                           # func name
    pait_id: str                             # pait id(in runtime)

    method_set: Optional[Set[str]] = None    # request method set
    path: Optional[str] = None               # request path
    operation_id: Optional[str] = None       # operation id(in route table)

    author: Optional[Tuple[str]] = None      # author
    desc: InitVar[str] = None                # description
    status: Optional[PaitStatus] = None      # api status. example: test, release
    group: str = 'root'                        # request tag
    tag: Optional[Tuple[str, ...]] = None

    response_model_list: List[Type[PaitResponseModel]] = None

    def __post_init__(self, desc: InitVar[str]):
        if desc:
            self.desc = desc
        else:
            self.desc = self.func.__doc__


@dataclass()
class FuncSig:
    func: Callable
    sig: 'inspect.Signature'
    param_list: List['inspect.Parameter']
