from dataclasses import dataclass

from pait.grpc.grpc_inspect import GrpcServiceOptionModel


@dataclass()
class GrpcModel(object):
    index: int
    func_name: str
    grpc_method_url: str
    template_dict: dict
    grpc_service_option_model: GrpcServiceOptionModel
    # func: Callable
