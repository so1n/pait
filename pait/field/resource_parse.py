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


class ParseResourceFuncProtocol(Protocol):
    """
    param rule func only run in ParamHandler, (Usually it will only be called in 'prd_handle')
    """

    def __call__(self, pr: "ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
        pass


@dataclass
class PreLoadDc(object):
    call_handler: "CallType"
    param: "ParseResourceParamDcDict" = dc_field(default_factory=dict)
    cbv_param: Optional["ParseResourceParamDcDict"] = dc_field(default=None)


@dataclass
class ParseResourceParamDc(object):
    name: str
    annotation: type
    parameter: inspect.Parameter
    parse_resource_func: ParseResourceFuncProtocol
    sub: "PreLoadDc" = dc_field(default_factory=lambda: PreLoadDc(call_handler=empty_pr_func))


ParseResourceParamDcDict = Dict[str, "ParseResourceParamDc"]


#############################
# Base Request Value Handle #
#############################
def get_real_request_value(parameter: inspect.Parameter, request_value: Mapping) -> Any:
    """get request value by func param's request field"""
    pait_field: "BaseRequestResourceField" = parameter.default
    if pait_field.raw_return:
        if not request_value:
            if pait_field.default is not _pydanitc_adapter.PydanticUndefined:
                return pait_field.default
            elif pait_field.default_factory:
                return pait_field.default_factory()
    else:
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
def empty_pr_func(pr: "ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler") -> Any:
    """return MISSING, The representative could not get the requested value"""
    return MISSING


def request_field_get_value_pr_func(
    pr: "ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Mapping:
    """get request value by func param's request field"""
    request_value: Mapping = getattr(context.app_helper.request, pr.parameter.default.from_request(), lambda: {})()
    if request_value is None:
        request_value = {}
    return get_real_request_value(pr.parameter, request_value)


async def async_request_field_get_value_pr_func(
    pr: "ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
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
    pr: "ParseResourceParamDc",
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
    pr: "ParseResourceParamDc",
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
