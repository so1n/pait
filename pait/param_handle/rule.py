import asyncio
import inspect
from dataclasses import MISSING, dataclass
from dataclasses import field as dc_field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Mapping, Optional, Type, Union

from pydantic import BaseModel

from pait import _pydanitc_adapter
from pait._pydanitc_adapter import PydanticUndefined, is_v1
from pait.exceptions import NotFoundValueException
from pait.field import BaseRequestResourceField
from pait.types import CallType, Protocol

if TYPE_CHECKING:
    from pait.model.context import ContextModel

    from .base import BaseParamHandler


class ParamRuleFuncProtocol(Protocol):
    def __call__(
        self, pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler", **kwargs: Any
    ) -> Any:
        pass


#############################
# Base Request Value Handle #
#############################
def get_real_request_value(parameter: inspect.Parameter, request_value: Mapping) -> Any:
    pait_field: BaseRequestResourceField = parameter.default

    if not pait_field.raw_return:
        request_value = pait_field.request_value_handle(request_value)
        if request_value is PydanticUndefined:
            if pait_field.not_value_exception_func:
                raise pait_field.not_value_exception_func(parameter)
            else:
                raise NotFoundValueException(parameter.name, f"Can not found {parameter.name} value")
    return request_value


def flask_validate_request_value(
    parameter: inspect.Parameter, request_value: Mapping, pait_model_field: _pydanitc_adapter.PaitModelField
) -> Any:
    # TODO: try remove this func when flask version >=2.0.0
    annotation: Type[BaseModel] = parameter.annotation

    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        # validate by BaseModel
        return annotation(**request_value)
    else:
        # parse annotation is python type and pydantic.field
        if not is_v1 and isinstance(request_value, dict):
            # Fix _model_field.validate method not support like flask ImmutableMultiDict:
            #    e.g:
            #       intput: ImmutableMultiDict([('pin-code', '6666'), ('template-token', 'xxx')])
            #       output:{"pin-code": ["6666"], "template-token": ["xxx"]}
            #       But the desired result is: {"pin-code": "6666", "template-token": "xxx"}
            request_value = dict(request_value)
        return pait_model_field.validate(request_value)


def validate_request_value(
    parameter: inspect.Parameter, request_value: Mapping, pait_model_field: _pydanitc_adapter.PaitModelField
) -> Any:
    annotation: Type[BaseModel] = parameter.annotation

    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        # validate by BaseModel
        return annotation(**request_value)
    else:
        return pait_model_field.validate(request_value)


####################
# ParamRule Handle #
####################
def cbv_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    return context.app_helper.cbv_instance


def request_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    return context.app_helper.request.request


def pait_model_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    pait_model: Type[BaseModel] = pr.parameter.annotation
    _, kwargs = param_plugin.prd_handle(context, pait_model, pr.sub.param)
    return pait_model(**kwargs)


async def async_pait_model_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    pait_model: Type[BaseModel] = pr.parameter.annotation
    _, kwargs = await param_plugin.prd_handle(context, pait_model, pr.sub.param)  # type: ignore[misc]
    return pait_model(**kwargs)


def empty_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    return MISSING


def request_field_get_value_pr_func(
    pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Mapping:
    request_value: Mapping = getattr(context.app_helper.request, pr.parameter.default.get_field_name(), lambda: {})()
    return get_real_request_value(pr.parameter, request_value)


async def async_request_field_get_value_pr_func(
    pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    request_value: Union[Mapping, Coroutine[Any, Any, Mapping]] = getattr(
        context.app_helper.request, pr.parameter.default.get_field_name(), lambda: {}
    )()
    if asyncio.iscoroutine(request_value) or asyncio.isfuture(request_value):
        _request_value: Mapping = await request_value
    else:
        _request_value = request_value  # type: ignore[assignment]
    return get_real_request_value(pr.parameter, _request_value)


def request_field_pr_func(
    pr: "ParamRule",
    context: "ContextModel",
    param_plugin: "BaseParamHandler",
    *,
    pait_model_field: _pydanitc_adapter.PaitModelField,
    validate_request_value_cb: Callable[
        [inspect.Parameter, Mapping, _pydanitc_adapter.PaitModelField], Any
    ] = validate_request_value,
) -> Any:
    request_value = request_field_get_value_pr_func(pr, context, param_plugin)
    return validate_request_value_cb(pr.parameter, request_value, pait_model_field)


async def async_request_field_pr_func(
    pr: "ParamRule",
    context: "ContextModel",
    param_plugin: "BaseParamHandler",
    *,
    pait_model_field: _pydanitc_adapter.PaitModelField,
    validate_request_value_cb: Callable[
        [inspect.Parameter, Mapping, _pydanitc_adapter.PaitModelField], Any
    ] = validate_request_value,
) -> Any:
    request_value = await async_request_field_get_value_pr_func(pr, context, param_plugin)
    return validate_request_value_cb(pr.parameter, request_value, pait_model_field)


def request_depend_pr_func(
    pr: "ParamRule",
    context: "ContextModel",
    param_plugin: "BaseParamHandler",
    func_class_prd: Optional["ParamRuleDict"] = None,
) -> Any:
    return param_plugin.depend_handle(context, pr.sub, func_class_prd=func_class_prd)


@dataclass
class _FieldTypeDc(object):
    func: ParamRuleFuncProtocol
    async_func: ParamRuleFuncProtocol


class FieldTypeEnum(Enum):
    empty = _FieldTypeDc(empty_pr_func, empty_pr_func)  # type: ignore[arg-type]
    cbv_class = _FieldTypeDc(cbv_pr_func, cbv_pr_func)  # type: ignore[arg-type]
    request = _FieldTypeDc(request_pr_func, request_pr_func)  # type: ignore[arg-type]
    pait_model = _FieldTypeDc(pait_model_pr_func, async_pait_model_pr_func)  # type: ignore[arg-type]
    request_field = _FieldTypeDc(request_field_pr_func, async_request_field_pr_func)  # type: ignore[arg-type]
    request_depend = _FieldTypeDc(request_depend_pr_func, request_depend_pr_func)  # type: ignore[arg-type]


@dataclass
class ParamRule(object):
    name: str
    type_: type
    index: int
    parameter: inspect.Parameter
    param_func: ParamRuleFuncProtocol
    sub: "PreLoadDc"


@dataclass
class PreLoadDc(object):
    pait_handler: CallType
    pre_depend: List["PreLoadDc"] = dc_field(default_factory=list)
    param: "ParamRuleDict" = dc_field(default_factory=dict)


ParamRuleDict = Dict[str, "ParamRule"]
