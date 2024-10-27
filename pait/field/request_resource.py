import copy
import inspect
import warnings
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Tuple, Type, TypeVar, Union

from pydantic.fields import FieldInfo
from typing_extensions import deprecated  # type: ignore[attr-defined]
from typing_extensions import Annotated, TypedDict, Unpack

from pait import _pydanitc_adapter, rule
from pait.exceptions import NotFoundValueException
from pait.field.base import BaseField, ExtraParam
from pait.util import partial_wrapper

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel
    from pait.openapi.openapi import LinksModel
    from pait.param_handle.base import BaseParamHandler
    from pait.rule import FieldTypePrFuncDc, PreLoadDc

_regex_deprecated = deprecated("Deprecated in Pydantic v2, use `pattern` instead.")
_const_deprecated = deprecated("Deprecated in Pydantic v2")

_T = TypeVar("_T")
PydanticUndefined = _pydanitc_adapter.PydanticUndefined


class FieldBaseParamTypedDict(TypedDict, total=False):
    """
    :param links: OpenAPI Link model
    :param media_type: default media type of request body
    :param openapi_serialization: Additional description of OpenAPI Schema
    :param raw_return: If True, the return value will be returned as is (the request key will be invalidated).
    :param example: example data
    :param not_value_exception_func:
        The exception thrown when the corresponding value cannot be obtained from the request,
        default value `_default_not_value_exception_func`
    :param openapi_include: Whether it is used by the OpenAPI
    :param extra_param_list: Extended parameters for plug-ins to use
    """

    links: "Optional[LinksModel]"
    media_type: str
    openapi_serialization: Any
    raw_return: bool
    example: Any
    not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]]
    openapi_include: bool
    extra_param_list: Optional[List[ExtraParam]]
    # pydantic.Field param
    default_factory: Optional[Callable[[], Any]]
    alias: Optional[str]
    title: Optional[str]
    description: Optional[str]
    const: Annotated[Optional[bool], _const_deprecated]
    gt: Optional[float]
    ge: Optional[float]
    lt: Optional[float]
    le: Optional[float]
    multiple_of: Optional[float]
    min_items: Optional[int]
    max_items: Optional[int]
    min_length: Optional[int]
    max_length: Optional[int]
    regex: Annotated[Optional[str], _regex_deprecated]
    # pydantic v2 param
    pattern: Optional[str]
    validation_alias: Optional[str]
    serialization_alias: Optional[str]
    json_schema_extra: Union[Dict[str, Any], Callable[[Dict[str, Any]], None], None]
    extra: Any


def _check_param_value(v2_name: str, v1_name: str) -> None:
    raise ValueError(f"cannot specify both `{v2_name}` and `{v1_name}`, should use {v2_name}")  # pragma: no cover


def _default_not_value_exception_func(parameter: inspect.Parameter) -> Exception:
    param_name = parameter.name
    msg = f"Can not found {param_name} value"
    if isinstance(parameter.default, BaseRequestResourceField):
        msg += f" from {parameter.default.get_field_name()}"

    return NotFoundValueException(param_name, msg)


class BaseRequestResourceField(BaseField, FieldInfo):
    field_name: str = ""
    media_type: str = "*/*"
    openapi_serialization: Optional[dict] = None
    _from_request: str = ""

    def __init__(self, default: Any = PydanticUndefined, **kwargs: Unpack[FieldBaseParamTypedDict]):  # noqa:C901
        default_factory: Optional[Callable[[], Any]] = kwargs.pop("default_factory", None)
        not_value_exception_func: Optional[Callable[[inspect.Parameter], Exception]] = kwargs.pop(
            "not_value_exception_func", None
        )
        # Same checks as pydantic, checked in advance here
        if default is not PydanticUndefined and default_factory is not None:
            raise ValueError("cannot specify both default and default_factory")  # pragma: no cover
        if (default is not PydanticUndefined or default_factory is not None) and not_value_exception_func:
            raise ValueError(
                "cannot set not_value_exception_func when the parameter default or `default_factory` is not empty."
            )

        alias: Optional[str] = kwargs.pop("alias", None)
        if alias and not isinstance(alias, str):
            raise ValueError(f"alias type must str. not {alias}")

        # Reduce runtime judgments by preloading
        if default is not PydanticUndefined:
            self.request_value_handle = self.request_value_handle_by_default  # type: ignore
        elif default_factory is not None:
            self.request_value_handle = self.request_value_handle_by_default_factory  # type: ignore

        pait_extra_param = {}
        for copy_key in ("example", "links"):
            if copy_key in kwargs:
                pait_extra_param[copy_key] = kwargs.pop(copy_key, None)  # type: ignore[misc]

        #############################################
        # These parameters will not be used in self #
        #############################################
        self.openapi_include: bool = kwargs.pop("openapi_include", True)
        self.raw_return: bool = kwargs.pop("raw_return", False)
        self.not_value_exception_func: Callable[[inspect.Parameter], Exception] = (
            not_value_exception_func or _default_not_value_exception_func
        )
        self.media_type = kwargs.pop("media_type", self.__class__.media_type)
        # _state obj can fix pydantic v2 bug
        # e.g:
        #   request_value_handle_by_default and request_value_handle_by_default_factory method is dynamically set,
        #   so can't get the value through self:
        #       class DemoField(BaseRequestResourceField):
        #           def demo(self):
        #               assert self.request_key   x
        #   however, external calls can be obtained normally:
        #       Demo = Body()
        #       Demo.set_alias('demo')
        #       assert Demo.request_key == 'demo'  ✔

        # Note: if not alias, pait will set the key name to request_key in the preload phase
        self._state: dict = {"request_key": alias or ""}
        self.openapi_serialization = kwargs.pop("openapi_serialization", self.openapi_serialization)
        self.extra_param_list: List[ExtraParam] = kwargs.pop("extra_param_list", None) or []

        ##########################
        # pydantic V1 V2 adapter #
        ##########################
        min_items = kwargs.pop("min_items", None)
        max_items = kwargs.pop("max_items", None)
        min_length = kwargs.pop("min_length", None)
        max_length = kwargs.pop("max_length", None)
        regex = kwargs.pop("regex", None)
        pattern = kwargs.pop("pattern", None)
        json_schema_extra = kwargs.pop("json_schema_extra", None)
        validation_alias = kwargs.pop("validation_alias", None)
        serialization_alias = kwargs.pop("serialization_alias", None)
        const = kwargs.pop("const", None)
        real_kwargs = dict(
            default=default,
            default_factory=default_factory,
            alias=alias,
            title=kwargs.pop("title", None),
            description=kwargs.pop("description", None),
            gt=kwargs.pop("gt", None),
            ge=kwargs.pop("ge", None),
            lt=kwargs.pop("lt", None),
            le=kwargs.pop("le", None),
            multiple_of=kwargs.pop("multiple_of", None),
            min_items=min_items,
            max_items=max_items,
            min_length=min_length,
            max_length=max_length,
        )
        raw_extra = kwargs.pop("extra", None)
        extra: dict = kwargs  # type: ignore[assignment]
        if raw_extra:
            extra.update(raw_extra)
        if regex and pattern:
            _check_param_value("regex", "pattern")
        if _pydanitc_adapter.is_v1:
            if json_schema_extra:
                raise ValueError("Pydantic v1 not support `json_schema_extra`")
            real_kwargs["const"] = const
            real_kwargs["regex"] = pattern if pattern else regex

            if validation_alias:
                warnings.warn("Pydantic V1 not support param `validation_alias`")  # pragma: no cover
            if serialization_alias:
                warnings.warn("Pydantic V1 not support param `serialization_alias`")  # pragma: no cover
            extra.update(pait_extra_param)
        else:
            if regex:
                real_kwargs["pattern"] = regex
            if max_items:
                if max_length:
                    _check_param_value("max_items", "max_length")
                else:
                    real_kwargs["max_length"] = real_kwargs.pop("max_items")
            if min_items:
                if min_length:
                    _check_param_value("min_items", "min_length")
                else:
                    real_kwargs["min_length"] = real_kwargs.pop("min_items")

            real_kwargs["validation_alias"] = validation_alias or alias
            real_kwargs["serialization_alias"] = serialization_alias or alias

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
                    real_kwargs["json_schema_extra"] = json_schema_extra
                else:
                    real_kwargs["json_schema_extra"] = {}
                    if pait_extra_param:
                        real_kwargs["json_schema_extra"].update(pait_extra_param)
                    real_kwargs["json_schema_extra"].update(json_schema_extra)
            else:
                extra.update(pait_extra_param)
                real_kwargs["json_schema_extra"] = copy.deepcopy(extra)
        if extra:
            real_kwargs.update(extra)
        self._check_init_param(**real_kwargs)
        super().__init__(**real_kwargs)

    def _check_init_param(self, **kwargs: Any) -> None:
        """Different field class have different validation rules,
        and if you have your own validation requirements, need to implement them here"""

    def rule(
        self, param_handler: "Type[BaseParamHandler]", pait_core_model: "PaitCoreModel", parameter: "inspect.Parameter"
    ) -> "Tuple[FieldTypePrFuncDc, PreLoadDc]":
        rule_field_type = rule.request_field_ft
        parameter.default.set_request_key(parameter.name)
        validate_request_value_cb = rule.validate_request_value
        if pait_core_model.app_helper_class.app_name == "flask":
            validate_request_value_cb = rule.flask_validate_request_value
        rule_field_type_func_param_dict = dict(
            # Creating a model field is very performance-intensive (especially for Pydantic V2),
            # so it needs to be cached
            pait_model_field=_pydanitc_adapter.PaitModelField(
                value_name=parameter.name,
                annotation=parameter.annotation,
                field_info=parameter.default,
                request_param=parameter.default.get_field_name(),
            ),
            validate_request_value_cb=validate_request_value_cb,
        )
        rule_field_type = rule.FieldTypePrFuncDc(
            func=partial_wrapper(rule_field_type.func, **rule_field_type_func_param_dict),
            async_func=partial_wrapper(rule_field_type.async_func, **rule_field_type_func_param_dict),
        )
        return (
            rule_field_type,
            rule.PreLoadDc(pait_handler=rule.empty_pr_func),
        )

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
        return request_value.get(self.request_key, self.default_factory())  # type:ignore[misc]

    @property
    def links(self) -> "Optional[LinksModel]":
        return _pydanitc_adapter.get_field_extra_dict(self).get("links", None)

    @classmethod
    def get_field_name(cls) -> str:
        return cls.field_name or cls.__name__.lower()

    @classmethod
    def from_request(cls) -> str:
        return cls._from_request or cls.get_field_name()

    @classmethod
    def i(cls, default: Any = PydanticUndefined, **kwargs: Unpack[FieldBaseParamTypedDict]) -> Any:
        """ignore mypy tip"""
        return cls(default=default, **kwargs)

    @classmethod
    def t(  # type: ignore
        cls,
        default: _T = PydanticUndefined,
        example: _T = MISSING,  # type: ignore
        default_factory: Optional[Callable[[], _T]] = None,
        **kwargs: Unpack[FieldBaseParamTypedDict],
    ) -> _T:
        """Limited type hint support"""
        if getattr(example, "__class__", None) is not MISSING.__class__:
            kwargs["example"] = example
        kwargs["default_factory"] = default_factory
        return cls(default=default, **kwargs)  # type:ignore

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
            default=field.default,
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
    def _check_init_param(self, **kwargs: Any) -> None:
        if not (kwargs["default"] is PydanticUndefined and kwargs["default_factory"] is None):
            raise ValueError("The parameter of Path is required and does not support default values")


class Query(BaseRequestResourceField):
    pass


class MultiQuery(BaseRequestResourceField):
    pass
