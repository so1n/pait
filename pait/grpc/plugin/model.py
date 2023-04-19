from dataclasses import dataclass
from typing import TYPE_CHECKING

from pait.grpc import GrpcServiceOptionModel, MethodDescriptorProto, ServiceDescriptorProto

if TYPE_CHECKING:
    from pait.grpc.plugin.field_desc_proto_to_route_code import FileDescriptorProtoToRouteCode


@dataclass()
class GrpcModel(object):
    # meta data
    index: int
    attr_prefix: str
    filename: str
    gateway_name: str
    # real template value
    input_type_name: str
    output_type_name: str
    grpc_method_url: str
    method: str
    func_name: str
    request_message_model_name: str
    response_message_model_name: str
    request_message_name: str
    response_message_name: str
    stub_service_name: str
    service_name: str
    model_module_name: str
    message_module_name: str
    stub_module_name: str
    package: str
    response_class_name: str
    # option model
    grpc_service_option_model: GrpcServiceOptionModel
    # grpc descriptor
    grpc_descriptor_service: ServiceDescriptorProto
    grpc_descriptor_method: MethodDescriptorProto
    # plugin gen code
    gen_code: "FileDescriptorProtoToRouteCode"
