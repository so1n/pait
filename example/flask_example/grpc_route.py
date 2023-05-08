from __future__ import annotations

from functools import partial
from typing import Any

import grpc
from flask import Flask
from google.protobuf.json_format import MessageToDict  # type: ignore
from pydantic import BaseModel

from example.common.json_formant import parse_dict
from example.common.response_model import gen_response_model_handle
from example.flask_example.utils import create_app
from example.grpc_common.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto.other import other_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.grpc_common.python_example_proto_code.example_proto_by_option.book import (
    manager_pait_route,
    social_pait_route,
)
from example.grpc_common.python_example_proto_code.example_proto_by_option.other import other_pait_route
from example.grpc_common.python_example_proto_code.example_proto_by_option.user import user_pait_route
from pait.app import set_app_attribute
from pait.field import Header
from pait.grpc import GrpcGatewayRoute


def add_grpc_gateway_route(app: Flask) -> None:
    """Split out to improve the speed of test cases"""
    from typing import Callable, Type
    from uuid import uuid4

    from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2
    from pait.grpc import GrpcModel, Message

    def _make_response(resp_dict: dict) -> dict:
        return {"code": 0, "msg": "", "data": resp_dict}

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
            if grpc_model.grpc_method_url in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                def _route(
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
                        result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(self.channel).get_uid_by_token(
                            user_pb2.GetUidByTokenRequest(token=token)
                        )
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    request_msg: Message = self.msg_from_dict_handle(
                        grpc_model.request, request_dict, grpc_model.grpc_service_option_model.request_message.nested
                    )
                    # add req_id to request
                    grpc_msg: Message = func(request_msg, metadata=[("req_id", req_id)])
                    return self.msg_to_dict_handle(
                        grpc_msg,
                        grpc_model.grpc_service_option_model.response_message.exclude_column_name,
                        grpc_model.grpc_service_option_model.response_message.nested,
                    )

                return _route

    grpc_gateway_route: CustomerGrpcGatewayRoute = CustomerGrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        other_pb2_grpc.OtherStub,
        prefix="/api",
        title="Grpc",
        parse_msg_desc="by_mypy",
        gen_response_model_handle=gen_response_model_handle,
        make_response=_make_response,
        msg_to_dict=partial(MessageToDict, including_default_value_fields=True),
        parse_dict=parse_dict,
        import_name=__name__,
    )
    channel = grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000"))
    grpc_gateway_route.init_channel(channel)
    user_pait_route.StaticGrpcGatewayRoute(
        app,
        channel=channel,
        prefix="/api/static",
        title="static_user",
        make_response=_make_response,
        is_async=False,
        msg_to_dict=partial(MessageToDict, including_default_value_fields=True),
        parse_dict=parse_dict,
    )
    manager_pait_route.StaticGrpcGatewayRoute(
        app,
        channel=channel,
        prefix="/api/static",
        title="static_manager",
        make_response=_make_response,
        is_async=False,
        msg_to_dict=partial(MessageToDict, including_default_value_fields=True),
        parse_dict=parse_dict,
    )
    social_pait_route.StaticGrpcGatewayRoute(
        app,
        channel=channel,
        prefix="/api/static",
        title="static_social",
        make_response=_make_response,
        is_async=False,
        msg_to_dict=partial(MessageToDict, including_default_value_fields=True),
        parse_dict=parse_dict,
    )
    other_pait_route.StaticGrpcGatewayRoute(
        app,
        channel=channel,
        prefix="/api/static",
        title="static_other",
        make_response=_make_response,
        is_async=False,
        msg_to_dict=partial(MessageToDict, including_default_value_fields=True),
        parse_dict=parse_dict,
    )
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest


if __name__ == "__main__":
    with create_app(__name__) as app:
        add_grpc_gateway_route(app)
