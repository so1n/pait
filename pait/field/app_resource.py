from inspect import Parameter
from typing import TYPE_CHECKING, Any, Callable, Tuple, Type, TypeVar

from pait.field.base import BaseField
from pait.rule import FieldTypePrFuncDc
from pait.types import CallType, ParamSpec

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel
    from pait.param_handle.base import BaseParamHandler
    from pait.rule import ParamRule, PreLoadDc

P = ParamSpec("P")
R_T = TypeVar("R_T")


def request_depend_pr_func(
    pr: "ParamRule",
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

    def rule(
        self, param_handler: "Type[BaseParamHandler]", pait_core_model: "PaitCoreModel", parameter: "Parameter"
    ) -> "Tuple[FieldTypePrFuncDc, PreLoadDc]":
        return (
            FieldTypePrFuncDc(request_depend_pr_func, request_depend_pr_func),  # type: ignore[arg-type]
            param_handler._depend_pre_handle(pait_core_model, parameter.default.func),
        )
