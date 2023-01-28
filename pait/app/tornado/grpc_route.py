from google.protobuf.json_format import MessageToDict  # type: ignore
from google.protobuf.message import Message  # type: ignore
from typing_extensions import Self  # type: ignore

from pait.app.base.grpc_route import AsyncGrpcGatewayRoute as BaseGrpcRouter
from pait.app.tornado import pait as tornado_pait
from pait.app.tornado._simple_route import add_multi_simple_route


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = tornado_pait
    add_multi_simple_route = staticmethod(add_multi_simple_route)
