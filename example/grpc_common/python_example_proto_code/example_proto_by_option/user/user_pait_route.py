# This is an automatically generated file, please do not change
# gen by pait[0.7.8.3](https://github.com/so1n/pait)
from typing import Any, List, Type
from uuid import uuid4

from google.protobuf.empty_pb2 import Empty  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from pait import field
from pait.app.any import SimpleRoute, add_multi_simple_route, set_app_attribute
from pait.field import Header
from pait.g import pait_context
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from . import user_p2p, user_pb2, user_pb2_grpc


def get_uid_by_token_route(
    request_pydantic_model: user_p2p.GetUidByTokenRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: user_pb2_grpc.UserStub = pait_context.get().app_helper.get_attributes("gateway_attr_User")
    # check token
    result: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    request_msg: user_pb2.GetUidByTokenRequest = gateway.get_msg_from_dict(
        user_p2p.GetUidByTokenRequest, request_pydantic_model.dict()
    )
    grpc_msg: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def logout_user_route(
    request_pydantic_model: user_p2p.LogoutUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: user_pb2_grpc.UserStub = pait_context.get().app_helper.get_attributes("gateway_attr_User")
    request_dict: dict = request_pydantic_model.dict()
    request_dict["token"] = token
    request_msg: user_pb2.LogoutUserRequest = gateway.get_msg_from_dict(user_p2p.LogoutUserRequest, request_dict)
    grpc_msg: Empty = stub.logout_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def login_user_route(
    request_pydantic_model: user_p2p.LoginUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: user_pb2_grpc.UserStub = pait_context.get().app_helper.get_attributes("gateway_attr_User")
    # check token
    result: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    request_msg: user_pb2.LoginUserRequest = gateway.get_msg_from_dict(
        user_p2p.LoginUserRequest, request_pydantic_model.dict()
    )
    grpc_msg: user_pb2.LoginUserResult = stub.login_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def create_user_route(
    request_pydantic_model: user_p2p.CreateUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: user_pb2_grpc.UserStub = pait_context.get().app_helper.get_attributes("gateway_attr_User")
    # check token
    result: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    request_msg: user_pb2.CreateUserRequest = gateway.get_msg_from_dict(
        user_p2p.CreateUserRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.create_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def delete_user_route(
    request_pydantic_model: user_p2p.DeleteUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: user_pb2_grpc.UserStub = pait_context.get().app_helper.get_attributes("gateway_attr_User")
    # check token
    result: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    request_msg: user_pb2.DeleteUserRequest = gateway.get_msg_from_dict(
        user_p2p.DeleteUserRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.delete_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


class UserByOptionEmptyJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: dict = Field(description="api response data")

    name: str = "user_by_option_Empty"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class UserByOptionLoginUserResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: dict = Field(description="api response data")

    name: str = "user_by_option_LoginUserResult"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_gateway", self)
        set_app_attribute(self.app, "gateway_attr_User", user_pb2_grpc.UserStub(self.channel))
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait._response_model_list or []
        pait_logout_user_route = self._pait(
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user_by_option", ""),
            ),
            desc="",
            summary="User exit from the system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )(logout_user_route)
        pait_login_user_route = self._pait(
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user_by_option", ""),
            ),
            desc="",
            summary="User login to system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionLoginUserResultJsonResponseModel] + response_model_list,
        )(login_user_route)
        pait_create_user_route = self._pait(
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user-system", "grpc_user_service"),
                Tag("grpc-user_by_option", ""),
            ),
            desc="",
            summary="Create users through the system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )(create_user_route)
        pait_delete_user_route = self._pait(
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user-system", "grpc_user_service"),
                Tag("grpc-user_by_option", ""),
            ),
            desc="This interface performs a logical delete, not a physical delete",
            summary="",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )(delete_user_route)
        add_multi_simple_route(
            self.app,
            SimpleRoute(url="/user/logout", methods=["POST"], route=pait_logout_user_route),
            SimpleRoute(url="/user/login", methods=["POST"], route=pait_login_user_route),
            SimpleRoute(url="/user/create", methods=["POST"], route=pait_create_user_route),
            SimpleRoute(url="/user/delete", methods=["POST"], route=pait_delete_user_route),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
