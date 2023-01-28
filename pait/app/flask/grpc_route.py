from pait.app.base.grpc_route import GrpcGatewayRoute as BaseGrpcRouter
from pait.app.flask import pait
from pait.app.flask._simple_route import add_multi_simple_route as _add_multi_simple_route


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = pait
    add_multi_simple_route: staticmethod = staticmethod(_add_multi_simple_route)
