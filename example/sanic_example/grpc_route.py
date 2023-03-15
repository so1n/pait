from __future__ import annotations

from typing import Any

import grpc
from pydantic import BaseModel
from sanic import Sanic

from example.common.response_model import gen_response_model_handle
from example.grpc_common.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.sanic_example.utils import create_app
from pait.app import set_app_attribute
from pait.app.sanic.grpc_route import GrpcGatewayRoute
from pait.field import Header


def add_grpc_gateway_route(app: Sanic) -> None:
    """Split out to improve the speed of test cases"""
    from typing import Callable, Type
    from uuid import uuid4

    from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2
    from pait.grpc.grpc_inspect import GrpcModel, Message

    def _make_response(resp_dict: dict) -> dict:
        return {"code": 0, "msg": "", "data": resp_dict}

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
            if grpc_model.grpc_method_url in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                async def _route(
                    request_pydantic_model: request_pydantic_model_class,  # type: ignore
                    token: str = Header.i(description="User Token"),
                    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                ) -> Any:
                    func: Callable = self.get_grpc_func(grpc_model)
                    request_dict: dict = request_pydantic_model.dict()  # type: ignore
                    if grpc_model.grpc_method_url == "/user.User/logout_user":
                        # logout user need token param
                        request_dict["token"] = token
                    else:
                        # check token
                        result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(
                            self.channel
                        ).get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                    # add req_id to request
                    grpc_msg: Message = await func(request_msg, metadata=[("req_id", req_id)])
                    return self.make_response(self.msg_to_dict(grpc_msg))

                return _route

    grpc_gateway_route: CustomerGrpcGatewayRoute = CustomerGrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        prefix="/api",
        title="Grpc",
        parse_msg_desc="by_mypy",
        gen_response_model_handle=gen_response_model_handle,
        make_response=_make_response,
    )
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest

    def _before_server_start(*_: Any) -> None:
        grpc_gateway_route.init_channel(grpc.aio.insecure_channel("0.0.0.0:9000"))

    async def _after_server_stop(*_: Any) -> None:
        await grpc_gateway_route.channel.close()

    app.before_server_start(_before_server_start)

    app.after_server_stop(_after_server_stop)


if __name__ == "__main__":
    with create_app(__name__) as app:
        add_grpc_gateway_route(app)
