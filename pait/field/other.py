from inspect import Parameter
from typing import TYPE_CHECKING, Any, Type

from pydantic import BaseModel

from . import resource_parse
from .base import BaseField
from .util import get_parameter_list_from_pydantic_basemodel

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel
    from pait.param_handle import BaseParamHandler


#############
# --- CBV ---#
#############
def cbv_pr_func(
    pr: "resource_parse.ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    """get cbv from context"""
    return context.app_helper.cbv_instance


class CbvField(BaseField):
    @classmethod
    def pre_check(
        cls, core_model: "PaitCoreModel", parameter: Parameter, param_plugin: "Type[BaseParamHandler]"
    ) -> None:
        pass

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "Parameter", param_plugin: "Type[BaseParamHandler]"
    ) -> resource_parse.ParseResourceParamDc:
        return resource_parse.ParseResourceParamDc(
            name=parameter.name,
            annotation=parameter.annotation,
            parameter=parameter,
            parse_resource_func=cbv_pr_func,
        )


#################
# --- Request ---#
#################
def request_pr_func(
    pr: "resource_parse.ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    """get web framework request object from context"""
    return context.app_helper.request.request


class RequestField(BaseField):
    @classmethod
    def pre_check(
        cls, core_model: "PaitCoreModel", parameter: Parameter, param_plugin: "Type[BaseParamHandler]"
    ) -> None:
        pass

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "Parameter", param_plugin: "Type[BaseParamHandler]"
    ) -> resource_parse.ParseResourceParamDc:
        return resource_parse.ParseResourceParamDc(
            name=parameter.name,
            annotation=parameter.annotation,
            parameter=parameter,
            parse_resource_func=request_pr_func,
        )


####################
# --- Pait Model ---#
####################
def pait_model_pr_func(
    pr: "resource_parse.ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    """get pait model from ParamRule"""
    pait_model: Type[BaseModel] = pr.parameter.annotation
    # pait_model is ParamRule sub obj, so we need to call prd_handle to get the real value
    _, kwargs = param_plugin.prd_handle(context, pait_model, pr.sub.param)
    return pait_model(**kwargs)


async def async_pait_model_pr_func(
    pr: "resource_parse.ParseResourceParamDc", context: "ContextModel", param_plugin: "BaseParamHandler"
) -> Any:
    """get pait model from ParamRule"""
    pait_model: Type[BaseModel] = pr.parameter.annotation
    # pait_model is ParamRule sub obj, so we need to call prd_handle to get the real value
    _, kwargs = await param_plugin.prd_handle(context, pait_model, pr.sub.param)  # type: ignore[misc]
    return pait_model(**kwargs)


class PaitModelField(BaseField):

    @classmethod
    def pre_check(
        cls, core_model: "PaitCoreModel", parameter: Parameter, param_plugin: "Type[BaseParamHandler]"
    ) -> None:
        param_plugin.param_field_check_handler(
            core_model,
            parameter.annotation,
            get_parameter_list_from_pydantic_basemodel(
                parameter.annotation, default_field_class=core_model.default_field_class
            ),
        )

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "Parameter", param_plugin: "Type[BaseParamHandler]"
    ) -> resource_parse.ParseResourceParamDc:
        sub_pld = resource_parse.PreLoadDc(call_handler=resource_parse.empty_pr_func)
        param_list = get_parameter_list_from_pydantic_basemodel(
            parameter.annotation, default_field_class=core_model.default_field_class
        )
        sub_pld.param = param_plugin.get_param_rule_from_parameter_list(core_model, parameter.annotation, param_list)
        for _parameter in param_list:
            raw_name = _parameter.name
            # Each value in PaitModel does not need to valida by `pr func`
            sub_pld.param[raw_name].parse_resource_func = (
                resource_parse.async_request_field_get_value_pr_func  # type: ignore[assignment]
                if param_plugin.is_async_mode
                else resource_parse.request_field_get_value_pr_func
            )

            # If the value in Pait Model has alias, then the key of param should be alias
            real_name = _parameter.default.request_key
            if raw_name != real_name:
                sub_pld.param[real_name] = sub_pld.param.pop(raw_name)
        return resource_parse.ParseResourceParamDc(
            name=parameter.name,
            annotation=parameter.annotation,
            parameter=parameter,
            parse_resource_func=async_pait_model_pr_func if param_plugin.is_async_mode else pait_model_pr_func,
            sub=sub_pld,
        )
