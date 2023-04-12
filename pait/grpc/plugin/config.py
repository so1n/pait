from typing import Type

from protobuf_to_pydantic.plugin.config import ConfigModel as _ConfigModel
from pydantic import Field
from typing_extensions import Literal

from pait.grpc import DescTemplate
from pait.grpc.plugin.field_desc_proto_to_route_code import FileDescriptorProtoToRouteCode

GatewayModelLiteral = Literal["sync", "asyncio"]


class ConfigModel(_ConfigModel):
    desc_template: Type[DescTemplate] = Field(default=DescTemplate)
    gateway_model: GatewayModelLiteral = Field(
        default="sync",
        description=(
            "Specifies the gateway routing code to generate, currently only 'def' and 'async def' are supported"
        ),
    )
    file_descriptor_proto_to_route_code: Type[FileDescriptorProtoToRouteCode] = Field(
        default=FileDescriptorProtoToRouteCode
    )
    empty_type: Type = Field(
        default=dict,
        description=(
            "googl.protobuf.empty_pb2.Empty cannot be parsed by pydantic, and a type needs to be defined that"
            " can be resolved"
        ),
    )
    route_file_name_suffix: str = Field(
        default="_pait_route",
        description=(
            "The file name suffix, but not the file type. "
            "For example, if the name of the proto file is `book`, the generated file name is `book_p2p.py`"
        ),
    )
