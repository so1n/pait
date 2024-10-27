from inspect import Parameter
from typing import TYPE_CHECKING, Tuple, Type, TypeVar

from pait import rule
from pait.field.request_resource import File

from .util import BaseStream

_StreamT = TypeVar("_StreamT", bound=BaseStream)

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel
    from pait.param_handle.base import BaseParamHandler


def request_field_pr_func(
    pr: "rule.ParamRule",
    context: "ContextModel",
    param_plugin: "BaseParamHandler",
) -> BaseStream:
    stream_file: "StreamFile" = pr.parameter.default
    stream_class = pr.parameter.annotation
    request = context.app_helper.request
    stream = stream_class(request.header(), request.stream)
    stream.set_request_key(stream_file.request_key)
    return stream


class StreamFile(File):
    field_name: str = "file"

    def rule(
        self, param_handler: "Type[BaseParamHandler]", pait_core_model: "PaitCoreModel", parameter: "Parameter"
    ) -> "Tuple[rule.FieldTypePrFuncDc, rule.PreLoadDc]":
        parameter.default.set_request_key(parameter.name)
        # before check
        assert issubclass(parameter.annotation, BaseStream)
        return (
            rule.FieldTypePrFuncDc(request_field_pr_func, request_field_pr_func),  # type: ignore[arg-type]
            rule.PreLoadDc(pait_handler=rule.empty_pr_func),
        )
