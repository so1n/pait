from typing import Any

import grpc
from starlette.applications import Starlette

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
from pait.app import set_app_attribute
from pait.app.starlette import AddDocRoute
from pait.app.starlette.grpc_route import GrpcGatewayRoute
from pait.util.grpc_inspect.message_to_pydantic import grpc_timestamp_int_handler


def create_app() -> Starlette:
    app: Starlette = Starlette()
    grpc_gateway_route: GrpcGatewayRoute = GrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        prefix="/api",
        title="Grpc",
        grpc_timestamp_handler_tuple=(int, grpc_timestamp_int_handler),
        parse_msg_desc="by_mypy",
    )
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest

    def _before_server_start(*_: Any) -> None:
        grpc_gateway_route.init_channel(grpc.aio.insecure_channel("0.0.0.0:9000"))

    async def _after_server_stop(*_: Any) -> None:
        await grpc_gateway_route.channel.close()

    app.add_event_handler("startup", _before_server_start)
    app.add_event_handler("shutdown", _after_server_stop)
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc").gen_route(app)
    return app


if __name__ == "__main__":

    import uvicorn  # type: ignore

    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    uvicorn.run(create_app(), log_level="debug")
