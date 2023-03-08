from pait.app.base.grpc_route import AsyncGrpcGatewayRoute as BaseGrpcRouter
from pait.app.tornado import pait as tornado_pait
from pait.app.tornado._simple_route import add_multi_simple_route


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = tornado_pait
    add_multi_simple_route = staticmethod(add_multi_simple_route)
