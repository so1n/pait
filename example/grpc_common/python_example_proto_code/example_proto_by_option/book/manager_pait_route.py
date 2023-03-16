# This is an automatically generated file, please do not change
# gen by pait[0.7.8.3](https://github.com/so1n/pait)
from typing import Any, List, Type

from google.protobuf.empty_pb2 import Empty  # type: ignore
from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, Field, root_validator
from pydantic.fields import FieldInfo

from pait import field
from pait.app.any import SimpleRoute, add_multi_simple_route, set_app_attribute
from pait.field import Query
from pait.g import pait_context
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from . import manager_p2p, manager_pb2, manager_pb2_grpc


def create_book_route(request_pydantic_model: manager_p2p.CreateBookRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: manager_pb2_grpc.BookManagerStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookManager")
    request_msg: manager_pb2.CreateBookRequest = gateway.get_msg_from_dict(
        manager_p2p.CreateBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.create_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def delete_book_route(request_pydantic_model: manager_p2p.DeleteBookRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: manager_pb2_grpc.BookManagerStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookManager")
    request_msg: manager_pb2.DeleteBookRequest = gateway.get_msg_from_dict(
        manager_p2p.DeleteBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.delete_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_route(request_pydantic_model: manager_p2p.GetBookRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: manager_pb2_grpc.BookManagerStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookManager")
    request_msg: manager_pb2.GetBookRequest = gateway.get_msg_from_dict(
        manager_p2p.GetBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: manager_pb2.GetBookResult = stub.get_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_list_route(request_pydantic_model: manager_p2p.GetBookListRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: manager_pb2_grpc.BookManagerStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookManager")
    request_msg: manager_pb2.GetBookListRequest = gateway.get_msg_from_dict(
        manager_p2p.GetBookListRequest, request_pydantic_model.dict()
    )
    grpc_msg: manager_pb2.GetBookListResult = stub.get_book_list(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


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
        data: dict = Field(description="api response data")

    name: str = "book_manager_by_option_GetBookResult"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookManagerByOptionGetBookListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: dict = Field(description="api response data")

    name: str = "book_manager_by_option_GetBookListResult"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_gateway", self)
        set_app_attribute(self.app, "gateway_attr_BookManager", manager_pb2_grpc.BookManagerStub(self.channel))
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait._response_model_list or []
        pait_create_book_route = self._pait(
            name="",
            group="book_manager_by_option",
            append_tag=(Tag("grpc-book_manager_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionEmptyJsonResponseModel] + response_model_list,
        )(create_book_route)
        pait_delete_book_route = self._pait(
            name="",
            group="book_manager_by_option",
            append_tag=(Tag("grpc-book_manager_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionEmptyJsonResponseModel] + response_model_list,
        )(delete_book_route)
        pait_get_book_route = self._pait(
            name="",
            group="book_manager_by_option",
            append_tag=(Tag("grpc-book_manager_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionGetBookResultJsonResponseModel] + response_model_list,
        )(get_book_route)
        pait_get_book_list_route = self._pait(
            name="",
            group="book_manager_by_option",
            append_tag=(Tag("grpc-book_manager_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookManagerByOptionGetBookListResultJsonResponseModel] + response_model_list,
        )(get_book_list_route)
        add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/book_manager_by_option/BookManager/create_book", methods=["POST"], route=pait_create_book_route
            ),
            SimpleRoute(
                url="/book_manager_by_option/BookManager/delete_book", methods=["POST"], route=pait_delete_book_route
            ),
            SimpleRoute(
                url="/book_manager_by_option/BookManager/get_book", methods=["POST"], route=pait_get_book_route
            ),
            SimpleRoute(
                url="/book_manager_by_option/BookManager/get_book_list",
                methods=["POST"],
                route=pait_get_book_list_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
