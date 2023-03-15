# This is an automatically generated file, please do not change
# gen by pait[0.7.8.3](https://github.com/so1n/pait)
# type: ignore

from typing import Any, List, Type

from google.protobuf.empty_pb2 import Empty  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pait import field
from pait.app.any import SimpleRoute, add_multi_simple_route, set_app_attribute
from pait.field import Query
from pait.g import pait_context
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel, Field, root_validator
from pydantic.fields import FieldInfo

from . import manager_p2p, manager_pb2, manager_pb2_grpc, social_p2p, social_pb2, social_pb2_grpc


def like_book_route(request_pydantic_model: social_p2p.LikeBookRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: social_pb2_grpc.BookSocialStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookSocial")
    request_msg: social_pb2.LikeBookRequest = gateway.get_msg_from_dict(
        social_p2p.LikeBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.like_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def like_multi_book_route(request_pydantic_model: social_p2p.LikeBookMapRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: social_pb2_grpc.BookSocialStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookSocial")
    request_msg: social_pb2.LikeBookMapRequest = gateway.get_msg_from_dict(
        social_p2p.LikeBookMapRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.like_multi_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_like_route(request_pydantic_model: social_p2p.GetBookLikesRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: social_pb2_grpc.BookSocialStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookSocial")
    request_msg: social_pb2.GetBookLikesRequest = gateway.get_msg_from_dict(
        social_p2p.GetBookLikesRequest, request_pydantic_model.dict()
    )
    grpc_msg: social_pb2.GetBookLikesListResult = stub.get_book_like(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def comment_book_route(request_pydantic_model: social_p2p.CommentBookRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: social_pb2_grpc.BookSocialStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookSocial")
    request_msg: social_pb2.CommentBookRequest = gateway.get_msg_from_dict(
        social_p2p.CommentBookRequest, request_pydantic_model.dict()
    )
    grpc_msg: Empty = stub.comment_book(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


def get_book_comment_route(request_pydantic_model: social_p2p.GetBookCommentRequest) -> Any:
    gateway = pait_context.get().app_helper.get_attributes("gateway_attr_gateway")
    stub: social_pb2_grpc.BookSocialStub = pait_context.get().app_helper.get_attributes("gateway_attr_BookSocial")
    request_msg: social_pb2.GetBookCommentRequest = gateway.get_msg_from_dict(
        social_p2p.GetBookCommentRequest, request_pydantic_model.dict()
    )
    grpc_msg: social_pb2.GetBookCommentListResult = stub.get_book_comment(request_msg)
    return gateway.make_response(gateway.msg_to_dict(grpc_msg))


class BookSocialByOptionEmptyJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: None = Field(description="api response data")  # type: ignore

    name: str = "book_social_by_option_Empty"
    description: str = None.__doc__ or ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookSocialByOptionGetBookLikesListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: None = Field(description="api response data")  # type: ignore

    name: str = "book_social_by_option_GetBookLikesListResult"
    description: str = None.__doc__ or ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookSocialByOptionGetBookCommentListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: None = Field(description="api response data")  # type: ignore

    name: str = "book_social_by_option_GetBookCommentListResult"
    description: str = None.__doc__ or ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_gateway", self)
        set_app_attribute(self.app, "gateway_attr_BookSocial", social_pb2_grpc.BookSocialStub(self.channel))
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait._response_model_list or []
        pait_like_book_route = self._pait(
            name="",
            group="book_social_by_option",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )(like_book_route)
        pait_like_multi_book_route = self._pait(
            name="",
            group="book_social_by_option",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )(like_multi_book_route)
        pait_get_book_like_route = self._pait(
            name="",
            group="book",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="test additional bindings",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionGetBookLikesListResultJsonResponseModel] + response_model_list,
        )(get_book_like_route)
        pait_get_book_like_route_1 = self._pait(
            name="",
            group="book_social_by_option",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Query,
            response_model_list=[BookSocialByOptionGetBookLikesListResultJsonResponseModel] + response_model_list,
        )(get_book_like_route)
        pait_get_book_like_route_1.__name__ = "pait_get_book_like_route_1"
        pait_get_book_like_route_1.__qualname__ = pait_get_book_like_route_1.__qualname__.replace(
            "get_book_like_route", "pait_get_book_like_route_1"
        )
        pait_comment_book_route = self._pait(
            name="",
            group="book_social_by_option",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )(comment_book_route)
        pait_get_book_comment_route = self._pait(
            name="",
            group="book_social_by_option",
            append_tag=(Tag("grpc-book_social_by_option", ""),),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionGetBookCommentListResultJsonResponseModel] + response_model_list,
        )(get_book_comment_route)
        add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/book_social_by_option/BookSocial/like_book", methods=["POST"], route=pait_like_book_route
            ),
            SimpleRoute(
                url="/book_social_by_option/BookSocial/like_multi_book",
                methods=["POST"],
                route=pait_like_multi_book_route,
            ),
            SimpleRoute(url="/book/get-book-like", methods=["POST"], route=pait_get_book_like_route),
            SimpleRoute(
                url="/book_social_by_option/BookSocial/get_book_like", methods=["GET"], route=pait_get_book_like_route_1
            ),
            SimpleRoute(
                url="/book_social_by_option/BookSocial/comment_book", methods=["POST"], route=pait_comment_book_route
            ),
            SimpleRoute(
                url="/book_social_by_option/BookSocial/get_book_comment",
                methods=["POST"],
                route=pait_get_book_comment_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs
        )
