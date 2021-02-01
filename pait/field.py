from typing import Any, Callable, Optional

from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import NoArgAnyCallable


class BaseField(FieldInfo):
    def __init__(
        self,
        default: Any = Undefined,
        *,
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


class Body(BaseField):
    pass


class Cookie(BaseField):
    pass


class File(BaseField):
    pass


class Form(BaseField):
    pass


class Header(BaseField):
    pass


class Path(BaseField):
    pass


class Query(BaseField):
    pass


class Depends(object):
    def __init__(self, func: Callable):
        self.func: Callable = func
