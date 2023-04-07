# This is an automatically generated file, please do not change
# gen by pait[0.7.8.3](https://github.com/so1n/pait)
import asyncio
from typing import Any, Callable, List, Type

from google.protobuf.empty_pb2 import Empty  # type: ignore
from pydantic import BaseModel, Field

from pait import field
from pait.app.any import SimpleRoute, set_app_attribute
from pait.core import Pait
from pait.g import pait_context
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from . import manager_p2p, manager_pb2, manager_pb2_grpc


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

    name: str = "book_manager_by_option_GetBookResult"
    description: str = (
        manager_p2p.GetBookResult.__doc__ or "" if manager_p2p.GetBookResult.__module__ != "builtins" else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookManagerByOptionGetBookListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: manager_p2p.GetBookListResult = Field(description="api response data")

    name: str = "book_manager_by_option_GetBookListResult"
    description: str = (
        manager_p2p.GetBookListResult.__doc__ or "" if manager_p2p.GetBookListResult.__module__ != "builtins" else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


async def async_create_book_route(request_pydantic_model: manager_p2p.CreateBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.CreateBookRequest = gateway.get_msg_from_dict(
        manager_pb2.CreateBookRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.create_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: Empty = await gateway.BookManager_stub.create_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def create_book_route(request_pydantic_model: manager_p2p.CreateBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.CreateBookRequest = gateway.get_msg_from_dict(
        manager_pb2.CreateBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = gateway.BookManager_stub.create_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_delete_book_route(request_pydantic_model: manager_p2p.DeleteBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.DeleteBookRequest = gateway.get_msg_from_dict(
        manager_pb2.DeleteBookRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.delete_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: Empty = await gateway.BookManager_stub.delete_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def delete_book_route(request_pydantic_model: manager_p2p.DeleteBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.DeleteBookRequest = gateway.get_msg_from_dict(
        manager_pb2.DeleteBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = gateway.BookManager_stub.delete_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_get_book_route(request_pydantic_model: manager_p2p.GetBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.GetBookRequest = gateway.get_msg_from_dict(
        manager_pb2.GetBookRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.get_book, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: manager_pb2.GetBookResult = await gateway.BookManager_stub.get_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_route(request_pydantic_model: manager_p2p.GetBookRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.GetBookRequest = gateway.get_msg_from_dict(
        manager_pb2.GetBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: manager_pb2.GetBookResult = gateway.BookManager_stub.get_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


async def async_get_book_list_route(request_pydantic_model: manager_p2p.GetBookListRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.GetBookListRequest = gateway.get_msg_from_dict(
        manager_pb2.GetBookListRequest, request_pydantic_model.dict()
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookManager_stub.get_book_list, "_loop", None):
        raise RuntimeError(
            "Loop is not same, "
            "the grpc channel must be initialized after the event loop of the api server is initialized"
        )
    else:
        grpc_msg: manager_pb2.GetBookListResult = await gateway.BookManager_stub.get_book_list(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_list_route(request_pydantic_model: manager_p2p.GetBookListRequest) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_book_manager_by_option_gateway"
    )
    request_msg: manager_pb2.GetBookListRequest = gateway.get_msg_from_dict(
        manager_pb2.GetBookListRequest, request_pydantic_model.dict()
    )
    grpc_msg: manager_pb2.GetBookListResult = gateway.BookManager_stub.get_book_list(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    BookManager_stub: manager_pb2_grpc.BookManagerStub
    stub_str_list: List[str] = ["BookManager_stub"]

    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_book_manager_by_option_gateway", self)
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []
        create_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="book_manager_by_option-BookManager",
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
            group="book_manager_by_option-BookManager",
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
            group="book_manager_by_option-BookManager",
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
            group="book_manager_by_option-BookManager",
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
                url="/book_manager_by_option-BookManager/get_book",
                methods=["POST"],
                route=pait_async_get_book_route if self.is_async else pait_get_book_route,
            ),
            SimpleRoute(
                url="/book_manager_by_option-BookManager/get_book_list",
                methods=["POST"],
                route=pait_async_get_book_list_route if self.is_async else pait_get_book_list_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
