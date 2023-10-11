import copy
import inspect
import warnings
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, TypeVar, Union

from pydantic.fields import FieldInfo
from typing_extensions import deprecated  # type: ignore[attr-defined]
from typing_extensions import Annotated

from pait import _pydanitc_adapter
from pait.field.base import BaseField, ExtraParam

if TYPE_CHECKING:
    from pait.openapi.openapi import LinksModel

_regex_deprecated = deprecated("Deprecated in Pydantic v2, use `pattern` instead.")
_const_deprecated = deprecated("Deprecated in Pydantic v2")

_T = TypeVar("_T")
PydanticUndefined = _pydanitc_adapter.PydanticUndefined


def _check_param_value(v2_name: str, v1_name: str) -> None:
    raise ValueError(f"cannot specify both `{v2_name}` and `{v1_name}`, should use {v2_name}")  # pragma: no cover


class BaseRequestResourceField(BaseField, FieldInfo):
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
        not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]] = None,
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
        # pydantic v2 param
        pattern: Optional[str] = None,
        validation_alias: Optional[str] = None,
        serialization_alias: Optional[str] = None,
        json_schema_extra: Union[Dict[str, Any], Callable[[Dict[str, Any]], None], None] = None,
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
        if (default is not PydanticUndefined or default_factory is not None) and not_value_exception_func:
            raise ValueError(
                "cannot set not_value_exception_func when the parameter default or `default_factory` is not empty."
            )
        # Reduce runtime judgments by preloading
        if default is not PydanticUndefined:
            self.request_value_handle = self.request_value_handle_by_default  # type: ignore
        elif default_factory is not None:
            self.request_value_handle = self.request_value_handle_by_default_factory  # type: ignore

        pait_extra_param = {}
        if getattr(example, "__class__", None) is not MISSING.__class__:
            pait_extra_param["example"] = example
        if links:
            pait_extra_param["links"] = links

        #######################################################
        # These parameters will not be used in pydantic.Field #
        #######################################################
        self.openapi_include: bool = openapi_include
        self.raw_return = raw_return
        self.not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]] = not_value_exception_func
        self.media_type = media_type or self.__class__.media_type
        # _state obj can fix pydantic v2 bug
        # e.g:
        #   request_value_handle_by_default and request_value_handle_by_default_factory method is dynamically set,
        #   so can't get the value through self:
        #       self.request_key == ''
        #   but:
        #       Demo = Body()
        #       Demo.set_alias('demo')
        #       assert Demo.request_key == 'demo'

        # Note: if not alias, pait will set the key name to request_key in the preload phase
        self._state: dict = {"request_key": alias or ""}
        self.openapi_serialization = openapi_serialization or self.__class__.openapi_serialization
        self.extra_param_list: List[ExtraParam] = extra_param_list or []

        ##########################
        # pydantic V1 V2 adapter #
        ##########################
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
        if regex and pattern:
            _check_param_value("regex", "pattern")
        if _pydanitc_adapter.is_v1:
            if json_schema_extra:
                raise ValueError("Pydantic v1 not support `json_schema_extra`")
            kwargs["const"] = const
            kwargs["regex"] = pattern if pattern else regex

            if validation_alias:
                warnings.warn("Pydantic V1 not support param `validation_alias`")
            if serialization_alias:
                warnings.warn("Pydantic V1 not support param `serialization_alias`")
            extra.update(pait_extra_param)
        else:
            if regex:
                kwargs["pattern"] = regex
            if max_items:
                if max_length:
                    _check_param_value("max_items", "max_length")
                else:
                    kwargs["max_length"] = kwargs.pop("max_items")
            if min_items:
                if min_length:
                    _check_param_value("min_items", "min_length")
                else:
                    kwargs["min_length"] = kwargs.pop("min_items")

            kwargs["validation_alias"] = validation_alias or alias
            kwargs["serialization_alias"] = serialization_alias or alias

            # I don't want to write such complex code(T_T)
            # support pydantic version (2.0.x, 2.1.x, 2.2.x+)
            if json_schema_extra:
                if callable(json_schema_extra):
                    if extra:
                        raise ValueError("If the value of `json_schema_extra` is callable, then `extra` must be empty")
                    if pait_extra_param:
                        pait_extra_param_name = ",".join(list(pait_extra_param.keys()))
                        raise ValueError(
                            f"If the value of `json_schema_extra` is callable,"
                            f" then {pait_extra_param_name}  must be empty"
                        )
                    kwargs["json_schema_extra"] = json_schema_extra
                else:
                    kwargs["json_schema_extra"] = {}
                    if pait_extra_param:
                        kwargs["json_schema_extra"].update(pait_extra_param)
                    kwargs["json_schema_extra"].update(json_schema_extra)
            else:
                extra.update(pait_extra_param)
                kwargs["json_schema_extra"] = copy.deepcopy(extra)
        if extra:
            kwargs.update(extra)
        super().__init__(**kwargs)

    @property
    def request_key(self) -> str:
        return self._state.get("request_key", "")

    def set_alias(self, value: Optional[str]) -> None:
        """reset field alias,
        In pydantic V2, if the model has been initialized, the `set_alias` method will be invalid.
        """
        self.alias = value
        if not _pydanitc_adapter.is_v1:
            self.validation_alias = value
            self.serialization_alias = value
        if value is not None:
            self._state["request_key"] = value

    def set_request_key(self, request_key: str) -> None:
        if not self.alias:
            self._state["request_key"] = request_key

    def request_value_handle(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, PydanticUndefined)

    def request_value_handle_by_default(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, self.default)

    def request_value_handle_by_default_factory(self, request_value: Mapping) -> Any:
        return request_value.get(self.request_key, self.default_factory())

    @property
    def links(self) -> "Optional[LinksModel]":
        return _pydanitc_adapter.get_field_extra_dict(self).get("links", None)

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
        not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]] = None,
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
        json_schema_extra: Union[Dict[str, Any], Callable[[Dict[str, Any]], None], None] = None,
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
            not_value_exception_func=not_value_exception_func,
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
            json_schema_extra=json_schema_extra,
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
        not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]] = None,
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
        json_schema_extra: Union[Dict[str, Any], Callable[[Dict[str, Any]], None], None] = None,
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
            not_value_exception_func=not_value_exception_func,
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
            json_schema_extra=json_schema_extra,
            **extra,
        )

    @classmethod
    def from_pydantic_field(cls, field: FieldInfo) -> "BaseRequestResourceField":
        """use replace pydantic property field"""
        extra_dict = _pydanitc_adapter.get_field_extra_dict(field)
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


class Json(BaseRequestResourceField):
    media_type: str = "application/json"
    field_name = "body"


class Body(Json):
    """Compatible with the old interface, it may be removed in the future"""


class Cookie(BaseRequestResourceField):
    pass


class File(BaseRequestResourceField):
    media_type: str = "multipart/form-data"


class Form(BaseRequestResourceField):
    media_type: str = "application/x-www-form-urlencoded"


class MultiForm(BaseRequestResourceField):
    media_type: str = "application/x-www-form-urlencoded"
    openapi_serialization: Optional[dict] = {"style": "form", "explode": True}


class Header(BaseRequestResourceField):
    pass


class Path(BaseRequestResourceField):
    pass


class Query(BaseRequestResourceField):
    pass


class MultiQuery(BaseRequestResourceField):
    pass
