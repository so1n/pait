# This is an automatically generated file, please do not change
# gen by pait[0.7.8.3](https://github.com/so1n/pait)
import asyncio
from typing import Any, Callable, List, Type
from uuid import uuid4

from google.protobuf.empty_pb2 import Empty  # type: ignore
from pydantic import BaseModel, Field

from pait import field
from pait.app.any import SimpleRoute, set_app_attribute
from pait.core import Pait
from pait.field import Header
from pait.g import pait_context
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from . import user_p2p, user_pb2, user_pb2_grpc


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
        data: user_p2p.LoginUserResult = Field(description="api response data")

    name: str = "user_by_option_LoginUserResult"
    description: str = (
        user_p2p.LoginUserResult.__doc__ or "" if user_p2p.LoginUserResult.__module__ != "builtins" else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


async def async_logout_user_route(
    request_pydantic_model: user_p2p.LogoutUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_dict: dict = request_pydantic_model.dict()
    request_dict["token"] = token
    request_msg: user_pb2.LogoutUserRequest = gateway.get_msg_from_dict(user_pb2.LogoutUserRequest, request_dict)
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.User_stub.logout_user, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: Empty = await gateway.User_stub.logout_user(request_msg, metadata=[("req_id", req_id)])
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def logout_user_route(
    request_pydantic_model: user_p2p.LogoutUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_dict: dict = request_pydantic_model.dict()
    request_dict["token"] = token
    request_msg: user_pb2.LogoutUserRequest = gateway.get_msg_from_dict(user_pb2.LogoutUserRequest, request_dict)
    grpc_msg: Empty = gateway.User_stub.logout_user(request_msg, metadata=[("req_id", req_id)])
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_login_user_route(request_pydantic_model: user_p2p.LoginUserRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_msg: user_pb2.LoginUserRequest = gateway.get_msg_from_dict(
        user_pb2.LoginUserRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.User_stub.login_user, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: user_pb2.LoginUserResult = await gateway.User_stub.login_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def login_user_route(request_pydantic_model: user_p2p.LoginUserRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_msg: user_pb2.LoginUserRequest = gateway.get_msg_from_dict(
        user_pb2.LoginUserRequest, request_pydantic_model.dict()
    )
    grpc_msg: user_pb2.LoginUserResult = gateway.User_stub.login_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_create_user_route(request_pydantic_model: user_p2p.CreateUserRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_msg: user_pb2.CreateUserRequest = gateway.get_msg_from_dict(
        user_pb2.CreateUserRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.User_stub.create_user, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: Empty = await gateway.User_stub.create_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def create_user_route(request_pydantic_model: user_p2p.CreateUserRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    request_msg: user_pb2.CreateUserRequest = gateway.get_msg_from_dict(
        user_pb2.CreateUserRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = gateway.User_stub.create_user(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_delete_user_route(
    request_pydantic_model: user_p2p.DeleteUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    stub: user_pb2_grpc.UserStub = gateway.User_stub
    request_msg: user_pb2.DeleteUserRequest = gateway.get_msg_from_dict(
        user_pb2.DeleteUserRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.User_stub.delete_user, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    # check token
    result: user_pb2.GetUidByTokenResult = await stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = await stub.delete_user(request_msg, metadata=[("req_id", req_id)])
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def delete_user_route(
    request_pydantic_model: user_p2p.DeleteUserRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_user_by_option_gateway"
    )
    stub: user_pb2_grpc.UserStub = gateway.User_stub
    request_msg: user_pb2.DeleteUserRequest = gateway.get_msg_from_dict(
        user_pb2.DeleteUserRequest, request_pydantic_model.dict()
    )
    # check token
    result: user_pb2.GetUidByTokenResult = stub.get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.delete_user(request_msg, metadata=[("req_id", req_id)])
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    User_stub: user_pb2_grpc.UserStub
    stub_str_list: List[str] = ["User_stub"]

    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_user_by_option_gateway", self)
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []
        logout_user_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user_by_option-User", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="User exit from the system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_logout_user_route = logout_user_route_pait(feature_code="0")(async_logout_user_route)
        pait_logout_user_route = logout_user_route_pait(feature_code="0")(logout_user_route)
        login_user_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user_by_option-User", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="User login to system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionLoginUserResultJsonResponseModel] + response_model_list,
        )
        pait_async_login_user_route = login_user_route_pait(feature_code="0")(async_login_user_route)
        pait_login_user_route = login_user_route_pait(feature_code="0")(login_user_route)
        create_user_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user-system", "grpc_user_service"),
                Tag("grpc-user_by_option-User", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="Create users through the system",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_create_user_route = create_user_route_pait(feature_code="0")(async_create_user_route)
        pait_create_user_route = create_user_route_pait(feature_code="0")(create_user_route)
        delete_user_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="user",
            append_tag=(
                Tag("grpc-user", "grpc_user_service"),
                Tag("grpc-user-system", "grpc_user_service"),
                Tag("grpc-user_by_option-User", ""),
                self._grpc_tag,
            ),
            desc="This interface performs a logical delete, not a physical delete",
            summary="",
            default_field_class=field.Body,
            response_model_list=[UserByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_delete_user_route = delete_user_route_pait(feature_code="0")(async_delete_user_route)
        pait_delete_user_route = delete_user_route_pait(feature_code="0")(delete_user_route)
        self._add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/user/logout",
                methods=["POST"],
                route=pait_async_logout_user_route if self.is_async else pait_logout_user_route,
            ),
            SimpleRoute(
                url="/user/login",
                methods=["POST"],
                route=pait_async_login_user_route if self.is_async else pait_login_user_route,
            ),
            SimpleRoute(
                url="/user/create",
                methods=["POST"],
                route=pait_async_create_user_route if self.is_async else pait_create_user_route,
            ),
            SimpleRoute(
                url="/user/delete",
                methods=["POST"],
                route=pait_async_delete_user_route if self.is_async else pait_delete_user_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
