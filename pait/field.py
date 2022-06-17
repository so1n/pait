from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import NoArgAnyCallable

if TYPE_CHECKING:
    from pait.model.links import LinksModel


class BaseField(FieldInfo):
    field_name: str = ""
    media_type: str = "*/*"
    openapi_serialization: Optional[dict] = None

    def __init__(
        self,
        default: Any = Undefined,
        *,
        link: "Optional[LinksModel]" = None,
        media_type: str = "",
        openapi_serialization: Any = None,
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

        # Same checks as pydantic, checked in advance here
        if default is not Undefined and default_factory is not None:
            raise ValueError("cannot specify both default and default_factory")  # pragma: no cover

        # Reduce runtime judgments by preloading
        if default is not Undefined:
            self.request_value_handle = self.request_value_handle_by_default  # type: ignore
        elif default_factory is not None:
            self.request_value_handle = self.request_value_handle_by_default_factory  # type: ignore

        self.raw_return = raw_return
        if getattr(example, "__class__", None) is not MISSING.__class__:
            extra["example"] = example

        if not link:
            link = extra.pop("link", None)
        self.link: "Optional[LinksModel]" = link

        self.media_type = media_type or self.__class__.media_type
        # if not alias, pait will set the key name to request_key in the preload phase
        self.request_key: Optional[str] = alias
        self.openapi_serialization = openapi_serialization or self.__class__.openapi_serialization
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

    def request_value_handle(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, Undefined)

    def request_value_handle_by_default(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, self.default)

    def request_value_handle_by_default_factory(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, self.default_factory())

    @classmethod
    def get_field_name(cls) -> str:
        return cls.field_name or cls.__name__.lower()

    @classmethod
    def i(
        cls,
        default: Any = Undefined,
        *,
        link: "Optional[LinksModel]" = None,
        raw_return: bool = False,
        media_type: str = "",
        example: Any = MISSING,
        openapi_serialization: Any = None,
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
            link=link,
            example=example,
            media_type=media_type,
            openapi_serialization=openapi_serialization,
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
    def from_pydantic_field(cls, field: FieldInfo) -> "BaseField":
        """use replace pydantic property field"""
        return cls(
            field.default,
            default_factory=field.default_factory,
            alias=field.alias,
            title=field.title,
            description=field.description,
            const=field.const,
            gt=field.gt,
            ge=field.ge,
            lt=field.lt,
            le=field.le,
            multiple_of=field.multiple_of,
            min_items=field.min_items,
            max_items=field.max_items,
            min_length=field.min_length,
            max_length=field.max_length,
            regex=field.regex,
            **field.extra,
        )


class Body(BaseField):
    media_type: str = "application/json"


class Cookie(BaseField):
    pass


class File(BaseField):
    media_type: str = "multipart/form-data"


class Form(BaseField):
    media_type: str = "application/x-www-form-urlencoded"


class MultiForm(BaseField):
    media_type: str = "application/x-www-form-urlencoded"
    openapi_serialization: Optional[dict] = {"style": "form", "explode": True}


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


def is_pait_field(pait_field: Any) -> bool:
    return isinstance(pait_field, (BaseField, Depends))


def is_pait_field_class(pait_field: Any) -> bool:
    return issubclass(pait_field, (BaseField, Depends))
