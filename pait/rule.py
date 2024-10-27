import asyncio
import inspect
from dataclasses import MISSING, dataclass
from dataclasses import field as dc_field
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Mapping, Optional, Type, Union

from pydantic import BaseModel

from pait import _pydanitc_adapter
from pait.types import Protocol

if TYPE_CHECKING:
    from pait.field import BaseRequestResourceField
    from pait.model.context import ContextModel
    from pait.param_handle.base import BaseParamHandler
    from pait.types import CallType


class ParamRuleFuncProtocol(Protocol):
    """
    param rule func only run in ParamHandler, (Usually it will only be called in 'prd_handle')
    """

    def __call__(
        self, pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler", **kwargs: Any
    ) -> Any:
        pass


@dataclass
class FieldTypePrFuncDc(object):
    func: ParamRuleFuncProtocol
    async_func: ParamRuleFuncProtocol


@dataclass
class ParamRule(object):
    name: str
    type_: type
    parameter: inspect.Parameter
    param_func: ParamRuleFuncProtocol
    sub: "PreLoadDc"


@dataclass
class PreLoadDc(object):
    pait_handler: "CallType"
    param: "ParamRuleDict" = dc_field(default_factory=dict)
    func_class_prd: Optional["ParamRuleDict"] = dc_field(default=None)


ParamRuleDict = Dict[str, "ParamRule"]


#############################
# Base Request Value Handle #
#############################
def get_real_request_value(parameter: inspect.Parameter, request_value: Mapping) -> Any:
    """get request value by func param's request field"""
    pait_field: "BaseRequestResourceField" = parameter.default

    if not pait_field.raw_return:
        request_value = pait_field.request_value_handle(request_value)
        if request_value is _pydanitc_adapter.PydanticUndefined:
            raise pait_field.not_value_exception_func(parameter)
    return request_value


#################################
# Validate Request Value Handle #
#################################
def flask_validate_request_value(
    parameter: inspect.Parameter, request_value: Mapping, pait_model_field: _pydanitc_adapter.PaitModelField
) -> Any:
    annotation: Type[BaseModel] = parameter.annotation

    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        # validate by BaseModel
        return annotation(**request_value)
    else:
        # parse annotation is python type and pydantic.field
        if not _pydanitc_adapter.is_v1 and isinstance(request_value, dict):
            # Fix _model_field.validate method not support like flask ImmutableMultiDict:
            #    e.g:
            #       intput: ImmutableMultiDict([('pin-code', '6666'), ('template-token', 'xxx')])
            #       output:{"pin-code": ["6666"], "template-token": ["xxx"]}
            #       But the desired result is: {"pin-code": "6666", "template-token": "xxx"}
            request_value = dict(request_value)
        return pait_model_field.validate(request_value)


def validate_request_value(
    parameter: inspect.Parameter, request_value: Any, pait_model_field: _pydanitc_adapter.PaitModelField
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
    """get cbv from context"""
    return context.app_helper.cbv_instance


def request_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    """get web framework request object from context"""
    return context.app_helper.request.request


def pait_model_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    """get pait model from ParamRule"""
    pait_model: Type[BaseModel] = pr.parameter.annotation
    # pait_model is ParamRule sub obj, so we need to call prd_handle to get the real value
    _, kwargs = param_plugin.prd_handle(context, pait_model, pr.sub.param)
    return pait_model(**kwargs)


async def async_pait_model_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    """get pait model from ParamRule"""
    pait_model: Type[BaseModel] = pr.parameter.annotation
    # pait_model is ParamRule sub obj, so we need to call prd_handle to get the real value
    _, kwargs = await param_plugin.prd_handle(context, pait_model, pr.sub.param)  # type: ignore[misc]
    return pait_model(**kwargs)


def empty_pr_func(pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    """return MISSING, The representative could not get the requested value"""
    return MISSING


def request_field_get_value_pr_func(
    pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Mapping:
    """get request value by func param's request field"""
    request_value: Mapping = getattr(context.app_helper.request, pr.parameter.default.from_request(), lambda: {})()
    if request_value is None:
        request_value = {}
    return get_real_request_value(pr.parameter, request_value)


async def async_request_field_get_value_pr_func(
    pr: "ParamRule", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    """get request value by func param's request field"""
    request_value: Union[Mapping, Coroutine[Any, Any, Mapping]] = getattr(
        context.app_helper.request, pr.parameter.default.from_request(), lambda: {}
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
) -> Any:
    return param_plugin.depend_handle(context, pr.sub)


empty_ft = FieldTypePrFuncDc(empty_pr_func, empty_pr_func)  # type: ignore[arg-type]
cbv_class_ft = FieldTypePrFuncDc(cbv_pr_func, cbv_pr_func)  # type: ignore[arg-type]
request_ft = FieldTypePrFuncDc(request_pr_func, request_pr_func)  # type: ignore[arg-type]
pait_model_ft = FieldTypePrFuncDc(pait_model_pr_func, async_pait_model_pr_func)  # type: ignore[arg-type]
request_field_ft = FieldTypePrFuncDc(request_field_pr_func, async_request_field_pr_func)  # type: ignore[arg-type]
request_depend_ft = FieldTypePrFuncDc(request_depend_pr_func, request_depend_pr_func)  # type: ignore[arg-type]
