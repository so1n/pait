from __future__ import annotations

from typing import Any

import grpc
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

from example.common.response_model import gen_response_model_handle
from example.grpc_common.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.starlette_example.utils import api_exception
from pait.app import set_app_attribute
from pait.app.starlette.grpc_route import GrpcGatewayRoute
from pait.field import Header


def add_grpc_gateway_route(app: Starlette) -> None:
    """Split out to improve the speed of test cases"""
    from typing import Callable, Type
    from uuid import uuid4

    from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2
    from pait.util.grpc_inspect.stub import GrpcModel
    from pait.util.grpc_inspect.types import Message

    def _make_response(resp_dict: dict) -> Response:
        return JSONResponse({"code": 0, "msg": "", "data": resp_dict})

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:

            if grpc_model.method in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                async def _route(
                    request_pydantic_model: request_pydantic_model_class,  # type: ignore
                    token: str = Header.i(description="User Token"),
                    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                ) -> Any:
                    func: Callable = self.get_grpc_func(grpc_model.method)
                    request_dict: dict = request_pydantic_model.dict()  # type: ignore
                    if grpc_model.method == "/user.User/logout_user":
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
                    return self._make_response(self.get_dict_from_msg(grpc_msg))

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

    app.add_event_handler("startup", _before_server_start)
    app.add_event_handler("shutdown", _after_server_stop)


if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette

    from pait.app.starlette import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Starlette = Starlette()
    app.add_exception_handler(Exception, api_exception)
    add_grpc_gateway_route(app)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    uvicorn.run(app)
