import copy
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, Optional, TypeVar

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typing_extensions import deprecated  # type: ignore[attr-defined]
from typing_extensions import Annotated

from pait import _pydanitc_adapter
from pait.types import CallType, ParamSpec

if TYPE_CHECKING:
    from pait.openapi.openapi import LinksModel

_regex_deprecated = deprecated("Deprecated in Pydantic v2, use `pattern` instead.")
_const_deprecated = deprecated("Deprecated in Pydantic v2")

_T = TypeVar("_T")
PydanticUndefined = _pydanitc_adapter.PydanticUndefined


class ExtraParam(BaseModel):
    pass


class BaseField(FieldInfo):
    field_name: str = ""
    media_type: str = "*/*"
    openapi_serialization: Optional[dict] = None

    def __init__(
        self,
        default: Any = PydanticUndefined,
        *,
        links: "Optional[LinksModel]" = None,
        media_type: str = "",
        openapi_serialization: Any = None,
        raw_return: bool = False,
        example: Any = MISSING,
        not_value_exception: Optional[Exception] = None,
        openapi_include: bool = True,
        extra_param_list: Optional[List[ExtraParam]] = None,
        # pydantic.Field param
        default_factory: Optional[Callable[[], Any]] = None,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        const: Annotated[
            Optional[bool],
            _const_deprecated,
        ] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Annotated[Optional[str], _regex_deprecated] = None,
        pattern: Optional[str] = None,
        **extra: Any,
    ):
        """
        :param links: OpenAPI Link model
        :param media_type: default media type of request body
        :param openapi_serialization: Additional description of OpenAPI Schema
        :param raw_return: If True, the return value will be returned as is (the request key will be invalidated).
        :param example: example data
        :param not_value_exception:
            The exception thrown when the corresponding value cannot be obtained from the request,
            default value `pait.exceptions.NotFoundValueException`
        :param openapi_include: Whether it is used by the OpenAPI
        :param extra_param_list: Extended parameters for plug-ins to use
        """
        # Same checks as pydantic, checked in advance here
        if default is not PydanticUndefined and default_factory is not None:
            raise ValueError("cannot specify both default and default_factory")  # pragma: no cover

        # Reduce runtime judgments by preloading
        if default is not PydanticUndefined:
            self.request_value_handle = self.request_value_handle_by_default  # type: ignore
        elif default_factory is not None:
            self.request_value_handle = self.request_value_handle_by_default_factory  # type: ignore

        if getattr(example, "__class__", None) is not MISSING.__class__:
            extra["example"] = example
        if links:
            extra["links"] = links

        #######################################################
        # These parameters will not be used in pydantic.Field #
        #######################################################
        self.openapi_include: bool = openapi_include
        self.raw_return = raw_return
        self.not_value_exception: Optional[Exception] = not_value_exception
        self.media_type = media_type or self.__class__.media_type
        # if not alias, pait will set the key name to request_key in the preload phase
        self.request_key: str = alias or ""
        self.openapi_serialization = openapi_serialization or self.__class__.openapi_serialization
        self.extra_param_list: List[ExtraParam] = extra_param_list or []

        ##########################
        # pydantic V1 V2 adapter #
        ##########################
        if regex and pattern:
            raise ValueError("cannot specify both `regex` and `pattern`, should use pattern")  # pragma: no cover
        if _pydanitc_adapter.is_v1:
            extra["const"] = const
            if pattern:
                extra["regex"] = pattern
        else:
            if regex:
                extra["pattern"] = regex
            extra = {"json_schema_extra": copy.deepcopy(extra)}
        kwargs = dict(
            default=default,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            min_items=min_items,
            max_items=max_items,
            min_length=min_length,
            max_length=max_length,
        )
        if not _pydanitc_adapter.is_v1:
            # TODO support validation_alias and serialization_alias param
            kwargs["validation_alias"] = alias
            kwargs["serialization_alias"] = alias
            # validation_alias=alias,
            # serialization_alias=alias,

        kwargs.update(extra)
        super().__init__(**kwargs)

    def set_alias(self, value: Optional[str]) -> None:
        # TODO support validation_alias and serialization_alias param
        self.alias = value
        if value is not None:
            self.request_key = value

    #######################
    # Fix pydantic v2 bug #
    #######################
    # e.g:
    #   request_value_handle_by_default and request_value_handle_by_default_factory method is dynamically set,
    #   so can't get the value through self:
    #       self.request_key == ''
    #   but:
    #       Demo = Body()
    #       Demo.set_alias('demo')
    #       assert Demo.request_key == 'demo'
    def request_value_handle(self, request_value: Mapping, request_key: str = "") -> Any:
        return request_value.get(request_key or self.request_key, PydanticUndefined)

    def request_value_handle_by_default(self, request_value: Mapping, request_key: str = "") -> Any:
        return request_value.get(request_key or self.request_key, self.default)

    def request_value_handle_by_default_factory(self, request_value: Mapping, request_key: str = "") -> Any:
        return request_value.get(request_key or self.request_key, self.default_factory())

    @property
    def links(self) -> "Optional[LinksModel]":
        return _pydanitc_adapter.get_field_extra(self).get("links", None)

    @classmethod
    def get_field_name(cls) -> str:
        return cls.field_name or cls.__name__.lower()

    @classmethod
    def i(
        cls,
        default: Any = PydanticUndefined,
        *,
        links: "Optional[LinksModel]" = None,
        raw_return: bool = False,
        media_type: str = "",
        example: Any = MISSING,
        openapi_serialization: Any = None,
        not_value_exception: Optional[Exception] = None,
        openapi_include: bool = True,
        default_factory: Optional[Callable[[], Any]] = None,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        const: Annotated[
            Optional[bool],
            _const_deprecated,
        ] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Annotated[Optional[str], _regex_deprecated] = None,
        pattern: Optional[str] = None,
        extra_param_list: Optional[List[ExtraParam]] = None,
        **extra: Any,
    ) -> Any:
        """ignore mypy tip"""
        return cls(
            default,
            raw_return=raw_return,
            links=links,
            example=example,
            media_type=media_type,
            openapi_serialization=openapi_serialization,
            not_value_exception=not_value_exception,
            openapi_include=openapi_include,
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
            pattern=pattern,
            extra_param_list=extra_param_list,
            **extra,
        )

    @classmethod
    def t(
        cls,
        default: _T = PydanticUndefined,
        *,
        links: "Optional[LinksModel]" = None,
        raw_return: bool = False,
        media_type: str = "",
        example: _T = MISSING,  # type: ignore
        openapi_serialization: Any = None,
        not_value_exception: Optional[Exception] = None,
        openapi_include: bool = True,
        default_factory: Optional[Callable[[], _T]] = None,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        const: Annotated[
            Optional[bool],
            _const_deprecated,
        ] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        multiple_of: Optional[float] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Annotated[
            Optional[str],
            _regex_deprecated,
        ] = None,
        pattern: Optional[str] = None,
        extra_param_list: Optional[List[ExtraParam]] = None,
        **extra: Any,
    ) -> _T:
        """Limited type hint support"""
        return cls(
            default,
            raw_return=raw_return,
            links=links,
            example=example,
            media_type=media_type,
            openapi_serialization=openapi_serialization,
            not_value_exception=not_value_exception,
            openapi_include=openapi_include,
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
            pattern=pattern,
            extra_param_list=extra_param_list,
            **extra,
        )

    @classmethod
    def from_pydantic_field(cls, field: FieldInfo) -> "BaseField":
        """use replace pydantic property field"""
        extra_dict = _pydanitc_adapter.get_field_extra(field)
        extra_dict["extra_param_list"] = extra_dict.pop("extra_param_list", None)
        if _pydanitc_adapter.is_v1:
            for key in [
                "const",
                "gt",
                "ge",
                "lt",
                "le",
                "multiple_of",
                "min_items",
                "max_items",
                "min_length",
                "max_length",
                "regex",
                "pattern",
            ]:
                value = getattr(field, key, None)
                if value is None:
                    continue
                extra_dict[key] = value
        else:
            param_key_set = {
                "const",
                "gt",
                "ge",
                "lt",
                "le",
                "multiple_of",
                "min_items",
                "max_items",
                "min_length",
                "max_length",
                "regex",
                "pattern",
            }
            for metadata in field.metadata:
                metadata_set = set(dir(metadata))
                for key in param_key_set & metadata_set:
                    extra_dict[key] = getattr(metadata, key)

        return cls(
            field.default,
            default_factory=field.default_factory,
            alias=field.alias,
            title=field.title,
            description=field.description,
            **extra_dict,
        )


class Json(BaseField):
    media_type: str = "application/json"
    field_name = "body"


class Body(Json):
    """Compatible with the old interface, it may be removed in the future"""


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


P = ParamSpec("P")
R_T = TypeVar("R_T")


class Depends(object):
    def __init__(self, func: CallType):
        self.func: CallType = func

    @classmethod
    def i(cls, func: CallType) -> Any:
        return cls(func)

    @classmethod
    def t(cls, func: Callable[P, R_T]) -> R_T:  # type: ignore
        return cls(func)  # type: ignore


def is_pait_field(pait_field: Any) -> bool:
    return isinstance(pait_field, (BaseField, Depends))


def is_pait_field_class(pait_field: Any) -> bool:
    return issubclass(pait_field, (BaseField, Depends))
