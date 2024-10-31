from inspect import Parameter
from typing import TYPE_CHECKING, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from pait.field.resource_parse import ParseResourceParamDc
    from pait.model.core import PaitCoreModel
    from pait.param_handle import BaseParamHandler


class BaseField(object):

    @classmethod
    def pre_check(
        cls, core_model: "PaitCoreModel", parameter: Parameter, param_plugin: Type["BaseParamHandler"]
    ) -> None:
        raise NotImplementedError

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "Parameter", param_plugin: Type["BaseParamHandler"]
    ) -> "ParseResourceParamDc":
        raise NotImplementedError


class ExtraParam(BaseModel):
    pass
