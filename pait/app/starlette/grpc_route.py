from pait.app.base.grpc_route import AsyncGrpcGatewayRoute as BaseGrpcRouter
from pait.app.starlette import pait
from pait.app.starlette._simple_route import add_multi_simple_route as _add_multi_simple_route


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = pait
    add_multi_simple_route: staticmethod = staticmethod(_add_multi_simple_route)
