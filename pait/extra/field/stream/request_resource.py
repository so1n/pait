from inspect import Parameter
from typing import TYPE_CHECKING, Type, TypeVar

from pait.field import resource_parse
from pait.field.http import File

from .util import BaseStream

_StreamT = TypeVar("_StreamT", bound=BaseStream)

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel
    from pait.param_handle.base import BaseParamHandler


def request_field_pr_func(
    pr: "resource_parse.ParseResourceParamDc",
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

    @classmethod
    def pre_load(
        cls, core_model: "PaitCoreModel", parameter: "Parameter", param_plugin: "Type[BaseParamHandler]"
    ) -> resource_parse.ParseResourceParamDc:
        parameter.default.set_request_key(parameter.name)
        # before check
        assert issubclass(parameter.annotation, BaseStream)
        return resource_parse.ParseResourceParamDc(
            name=parameter.name,
            annotation=parameter.annotation,
            parameter=parameter,
            parse_resource_func=request_field_pr_func,
        )
