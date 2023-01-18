from importlib import import_module
from typing import TYPE_CHECKING

from pait.app.auto_load_app import auto_load_app_class

if TYPE_CHECKING:
    from pait.app.base.grpc_route import GrpcGatewayRoute as _GrpcGatewayRoute

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower()
GrpcGatewayRoute: "_GrpcGatewayRoute" = getattr(import_module(pait_app_path + ".grpc_route"), "GrpcGatewayRoute")
