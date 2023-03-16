from dataclasses import dataclass

from pait.grpc.grpc_inspect import GrpcServiceOptionModel
from pait.grpc.types import MethodDescriptorProto, ServiceDescriptorProto


@dataclass()
class GrpcModel(object):
    # meta data
    index: int
    attr_prefix: str
    # real template value
    grpc_method_url: str
    method: str
    func_name: str
    request_message: str
    response_message: str
    request_message_model: str
    response_message_model: str
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
