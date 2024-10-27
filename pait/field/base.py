from inspect import Parameter
from typing import TYPE_CHECKING, Tuple, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel
    from pait.param_handle.base import BaseParamHandler
    from pait.rule import FieldTypePrFuncDc, PreLoadDc


class BaseField(object):

    def rule(
        self, param_handler: "Type[BaseParamHandler]", pait_core_model: "PaitCoreModel", parameter: "Parameter"
    ) -> "Tuple[FieldTypePrFuncDc, PreLoadDc]":
        raise NotImplementedError


class ExtraParam(BaseModel):
    pass
