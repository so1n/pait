# This is an automatically generated file, please do not change
# gen by pait[0.0.0](https://github.com/so1n/pait)
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
from pait.grpc import rebuild_message, rebuild_message_type
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from ..user import user_pb2, user_pb2_grpc
from . import manager_p2p, manager_pb2, manager_pb2_grpc
from .manager_p2p import GetBookListResult as GetBookListResultGetBookListRoute
from .manager_p2p import GetBookRequest as GetBookRequestGetBookRoute

GetBookRequestGetBookRoute = rebuild_message(  # type: ignore[misc]
    GetBookRequestGetBookRoute,
    "get_book_route",
    exclude_column_name=["not_use_field1", "not_use_field2"],
    nested=[],
)


GetBookListResultGetBookListRoute = rebuild_message_type(  # type: ignore[misc]
    GetBookListResultGetBookListRoute,
    "get_book_list_route",
    exclude_column_name=[],
    nested=["result"],
)


class BookManagerByOptionEmptyJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: dict = Field(description="api response data")

    name: str = "book_manager_by_option_Empty"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookManagerByOptionGetBookResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: manager_p2p.GetBookResult = Field(description="api response data")

    name: str = "book_manager_by_option_manager_p2p.GetBookResult"
    description: str = (
        manager_p2p.GetBookResult.__doc__ or "" if manager_p2p.GetBookResult.__module__ != "builtins" else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookManagerByOptionGetBookListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: GetBookListResultGetBookListRoute = Field(description="api response data")

    name: str = "book_manager_by_option_GetBookListResultGetBookListRoute"
    description: str = (
        GetBookListResultGetBookListRoute.__doc__ or ""
        if GetBookListResultGetBookListRoute.__module__ != "builtins"
        else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


async def async_create_book_route(
    request_pydantic_model: manager_p2p.CreateBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.CreateBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.CreateBookRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.create_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    # check token
    result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = await stub.create_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def create_book_route(
    request_pydantic_model: manager_p2p.CreateBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.CreateBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.CreateBookRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.create_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_delete_book_route(
    request_pydantic_model: manager_p2p.DeleteBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.DeleteBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.DeleteBookRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.delete_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    # check token
    result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = await stub.delete_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def delete_book_route(
    request_pydantic_model: manager_p2p.DeleteBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.DeleteBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.DeleteBookRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.delete_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_get_book_route(
    request_pydantic_model: GetBookRequestGetBookRoute,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.GetBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.GetBookRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.get_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    # check token
    result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: manager_pb2.GetBookResult = await stub.get_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def get_book_route(
    request_pydantic_model: GetBookRequestGetBookRoute,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.GetBookRequest = gateway.msg_from_dict_handle(
        manager_pb2.GetBookRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: manager_pb2.GetBookResult = stub.get_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_get_book_list_route(
    request_pydantic_model: manager_p2p.GetBookListRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.GetBookListRequest = gateway.msg_from_dict_handle(
        manager_pb2.GetBookListRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.get_book_list, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    # check token
    result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: manager_pb2.GetBookListResult = await stub.get_book_list(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], ["result"])


def get_book_list_route(
    request_pydantic_model: manager_p2p.GetBookListRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/manager.proto_gateway"
    )
    stub: manager_pb2_grpc.BookManagerStub = gateway.BookManager_stub
    request_msg: manager_pb2.GetBookListRequest = gateway.msg_from_dict_handle(
        manager_pb2.GetBookListRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: manager_pb2.GetBookListResult = stub.get_book_list(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], ["result"])


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    BookManager_stub: manager_pb2_grpc.BookManagerStub
    stub_str_list: List[str] = ["BookManager_stub"]

    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_example_proto_by_option/book/manager.proto_gateway", self)
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []
        create_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_manager_by_option-BookManager", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_create_book_route = create_book_route_pait(feature_code="0")(async_create_book_route)
        pait_create_book_route = create_book_route_pait(feature_code="0")(create_book_route)
        delete_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_manager_by_option-BookManager", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_delete_book_route = delete_book_route_pait(feature_code="0")(async_delete_book_route)
        pait_delete_book_route = delete_book_route_pait(feature_code="0")(delete_book_route)
        get_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_manager_by_option-BookManager", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionGetBookResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_route = get_book_route_pait(feature_code="0")(async_get_book_route)
        pait_get_book_route = get_book_route_pait(feature_code="0")(get_book_route)
        get_book_list_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_manager_by_option-BookManager", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionGetBookListResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_list_route = get_book_list_route_pait(feature_code="0")(async_get_book_list_route)
        pait_get_book_list_route = get_book_list_route_pait(feature_code="0")(get_book_list_route)
        self._add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/book_manager_by_option-BookManager/create_book",
                methods=["POST"],
                route=pait_async_create_book_route if self.is_async else pait_create_book_route,
            ),
            SimpleRoute(
                url="/book_manager_by_option-BookManager/delete_book",
                methods=["POST"],
                route=pait_async_delete_book_route if self.is_async else pait_delete_book_route,
            ),
            SimpleRoute(
                url="/book/get",
                methods=["POST"],
                route=pait_async_get_book_route if self.is_async else pait_get_book_route,
            ),
            SimpleRoute(
                url="/book/get-list",
                methods=["POST"],
                route=pait_async_get_book_list_route if self.is_async else pait_get_book_list_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
