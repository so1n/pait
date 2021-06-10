from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, get_type_hints

from pydantic import BaseModel

from pait.util import create_pydantic_model

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class PaitStatus(Enum):
    """Interface life cycle"""

    undefined = "undefined"
    # The interface is under development and will frequently change
    design = "design"
    dev = "dev"

    # The interface has been completed, but there may be some bugs
    integration = "integration"
    complete = "complete"
    test = "test"

    # The interface is online
    pre_release = "pre_release"
    release = "release"

    # The interface has been online, but needs to be offline for some reasons
    abnormal = "abnormal"
    maintenance = "maintenance"
    archive = "archive"
    abandoned = "abandoned"


@dataclass()
class PaitResponseModel(object):
    """response model"""

    description: Optional[str] = ""
    header: dict = field(default_factory=dict)
    media_type: str = "application/json"
    response_data: Optional[Type[BaseModel]] = None
    status_code: List[int] = field(default_factory=lambda: [200])

    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.__class__.__name__


class PaitBaseModel(object):
    """pait base model, The value of the attribute supports filling in the pait field
    >>> from pait import field
    >>> class Demo(PaitBaseModel):
    ...     a: int = field.Query.i()
    ...     b: str = field.Body.i()
    """

    _pydantic_model: Optional[Type[BaseModel]] = None

    @classmethod
    def to_pydantic_model(cls) -> Type[BaseModel]:
        if cls._pydantic_model is not None:
            return cls._pydantic_model
        else:
            annotation_dict: Dict[str, Tuple[Type, Any]] = {
                param_name: (annotation, getattr(cls, param_name, ...))
                for param_name, annotation in get_type_hints(cls).items()
                if not param_name.startswith("_")
            }
            cls._pydantic_model = create_pydantic_model(annotation_dict)
            return cls._pydantic_model

    def dict(
        self,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        if self._pydantic_model is None:
            raise NotImplementedError
        _pydantic_model: BaseModel = self._pydantic_model(**self.__dict__)
        return _pydantic_model.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @classmethod
    def schema(cls, by_alias: bool = True) -> "DictStrAny":
        return cls.to_pydantic_model().schema(by_alias=by_alias)


class PaitCoreModel(object):
    def __init__(
        self,
        func: Callable,
        pait_id: str,
        path: Optional[str] = None,
        method_set: Optional[Set[str]] = None,
        operation_id: Optional[str] = None,
        func_name: Optional[str] = None,
        author: Optional[Tuple[str, ...]] = None,
        summary: Optional[str] = None,
        desc: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitResponseModel]]] = None,
    ):
        self.func: Callable = func  # route func
        self.pait_id: str = pait_id  # qualname + func hash id
        self.path: str = path or ""  # request url path
        self.method_list: List[str] = sorted(list(method_set or set()))  # request method set
        self.operation_id: Optional[str] = operation_id or None  # route name
        self.func_name: str = func_name or func.__name__
        self.author: Tuple[str, ...] = author or ("",)  # The main developer of this func
        self.summary: str = summary or ""
        self.desc: str = desc or func.__doc__ or ""  # desc of this func
        self.status: PaitStatus = status or PaitStatus.undefined  # Interface development progress (life cycle)
        self.group: str = group or "root"  # Which group this interface belongs to
        self.tag: Tuple[str, ...] = tag or ("default",)  # Interface tag
        self.response_model_list: Optional[List[Type[PaitResponseModel]]] = response_model_list
        self.func_path: str = ""
