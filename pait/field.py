from dataclasses import MISSING
from typing import Any, Callable, Optional

from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import NoArgAnyCallable


class BaseField(FieldInfo):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        raw_return: bool = False,
        example: Any = MISSING,
        default_factory: Optional[NoArgAnyCallable] = None,
        alias: str = None,
        title: str = None,
        description: str = None,
        const: bool = None,
        gt: float = None,
        ge: float = None,
        lt: float = None,
        le: float = None,
        multiple_of: float = None,
        min_items: int = None,
        max_items: int = None,
        min_length: int = None,
        max_length: int = None,
        regex: str = None,
        **extra: Any,
    ):
        if self.__class__.__mro__[2] != FieldInfo:
            raise RuntimeError("Only classes that inherit BaseField can be used")
        self.raw_return = raw_return
        self.lower_name: str = self.__class__.__name__.lower()
        if example is not MISSING:
            extra["example"] = example
        super().__init__(
            default,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            const=const,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            min_items=min_items,
            max_items=max_items,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            **extra,
        )

    @classmethod
    def cls_lower_name(cls) -> str:
        return cls.__name__.lower()

    def __lt__(self, other: "BaseField") -> bool:
        return self.lower_name < other.lower_name

    @classmethod
    def i(
        cls,
        default: Any = Undefined,
        *,
        raw_return: bool = False,
        example: Any = MISSING,
        default_factory: Optional[NoArgAnyCallable] = None,
        alias: str = None,
        title: str = None,
        description: str = None,
        const: bool = None,
        gt: float = None,
        ge: float = None,
        lt: float = None,
        le: float = None,
        multiple_of: float = None,
        min_items: int = None,
        max_items: int = None,
        min_length: int = None,
        max_length: int = None,
        regex: str = None,
        **extra: Any,
    ) -> Any:
        """ignore mypy tip"""
        return cls(
            default,
            raw_return=raw_return,
            example=example,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            const=const,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            min_items=min_items,
            max_items=max_items,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            **extra,
        )


class Body(BaseField):
    pass


class Cookie(BaseField):
    pass


class File(BaseField):
    pass


class Form(BaseField):
    pass


class MultiForm(BaseField):
    pass


class Header(BaseField):
    pass


class Path(BaseField):
    pass


class Query(BaseField):
    pass


class MultiQuery(BaseField):
    pass


class Depends(object):
    def __init__(self, func: Callable):
        self.func: Callable = func

    @classmethod
    def i(cls, func: Callable) -> Any:
        return cls(func)
