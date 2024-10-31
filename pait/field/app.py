import inspect
from typing import TYPE_CHECKING, Any, Callable, Type, TypeVar

from pait.exceptions import FieldValueTypeException
from pait.field.base import BaseField
from pait.field.resource_parse import ParseResourceParamDc
from pait.types import CallType, ParamSpec
from pait.util import FuncSig, get_func_sig, get_parameter_list_from_class, is_bounded_func, is_type

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel
    from pait.param_handle.base import BaseParamHandler

P = ParamSpec("P")
R_T = TypeVar("R_T")


def check_pre_depend(
    core_model: "PaitCoreModel", depend_func_sig: FuncSig, param_plugin: "Type[BaseParamHandler]"
) -> None:
    depend_func = depend_func_sig.func
    if inspect.ismethod(depend_func) and not is_bounded_func(depend_func):
        raise ValueError(f"Func: {depend_func} is not a function")

    param_plugin.param_field_check_handler(core_model, depend_func, depend_func_sig.param_list)
    if inspect.isclass(depend_func):
        param_plugin.param_field_check_handler(
            core_model,
            depend_func,
            get_parameter_list_from_class(depend_func),
        )


def request_depend_pr_func(
    pr: "ParseResourceParamDc",
    context: "ContextModel",
    param_plugin: "BaseParamHandler",
) -> Any:
    return param_plugin.depend_handle(context, pr.sub)


class Depends(BaseField):
    def __init__(self, func: CallType):
        self.func: CallType = func

    @classmethod
    def i(cls, func: CallType) -> Any:
        return cls(func)

    @classmethod
    def t(cls, func: Callable[P, R_T]) -> R_T:  # type: ignore
        return cls(func)  # type: ignore

    @classmethod
    def pre_check(
        cls, core_model: "PaitCoreModel", parameter: inspect.Parameter, param_plugin: "Type[BaseParamHandler]"
    ) -> None:
        depend_func = getattr(parameter.default, "func")
        func_sig: FuncSig = get_func_sig(depend_func)  # get and cache func sig
        check_pre_depend(core_model, func_sig, param_plugin)
        if not is_type(parameter.annotation, func_sig.return_param):
            raise FieldValueTypeException(
                parameter.name,
                f"{parameter.name}'s Depends.callable return annotation"
                f" must:{parameter.annotation}, not {func_sig.return_param}",
            )

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "inspect.Parameter", param_plugin: "Type[BaseParamHandler]"
    ) -> ParseResourceParamDc:
        return ParseResourceParamDc(
            name=parameter.name,
            annotation=parameter.annotation,
            parameter=parameter,
            parse_resource_func=request_depend_pr_func,
            sub=param_plugin.depend_handler(core_model, parameter.default.func),
        )
