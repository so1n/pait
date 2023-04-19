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
from pait.grpc import rebuild_message
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from ..user import user_pb2, user_pb2_grpc
from . import social_p2p, social_pb2, social_pb2_grpc
from .social_p2p import NestedGetBookLikesRequest as NestedGetBookLikesRequestGetBookLikeOtherRoute

NestedGetBookLikesRequestGetBookLikeOtherRoute = rebuild_message(  # type: ignore[misc]
    NestedGetBookLikesRequestGetBookLikeOtherRoute,
    "get_book_like_other_route",
    exclude_column_name=[],
    nested=["nested"],
)


class BookSocialByOptionEmptyJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: dict = Field(description="api response data")

    name: str = "book_social_by_option_Empty"
    description: str = dict.__doc__ or "" if dict.__module__ != "builtins" else ""
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookSocialByOptionGetBookLikesListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: social_p2p.GetBookLikesListResult = Field(description="api response data")

    name: str = "book_social_by_option_social_p2p.GetBookLikesListResult"
    description: str = (
        social_p2p.GetBookLikesListResult.__doc__ or ""
        if social_p2p.GetBookLikesListResult.__module__ != "builtins"
        else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


class BookSocialByOptionGetBookCommentListResultJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: social_p2p.GetBookCommentListResult = Field(description="api response data")

    name: str = "book_social_by_option_social_p2p.GetBookCommentListResult"
    description: str = (
        social_p2p.GetBookCommentListResult.__doc__ or ""
        if social_p2p.GetBookCommentListResult.__module__ != "builtins"
        else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


async def async_like_book_route(
    request_pydantic_model: social_p2p.LikeBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.LikeBookRequest = gateway.msg_from_dict_handle(
        social_pb2.LikeBookRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.like_book, "_loop", None):
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
    grpc_msg: Empty = await stub.like_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def like_book_route(
    request_pydantic_model: social_p2p.LikeBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.LikeBookRequest = gateway.msg_from_dict_handle(
        social_pb2.LikeBookRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.like_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_like_multi_book_route(
    request_pydantic_model: social_p2p.LikeBookMapRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.LikeBookMapRequest = gateway.msg_from_dict_handle(
        social_pb2.LikeBookMapRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.like_multi_book, "_loop", None):
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
    grpc_msg: Empty = await stub.like_multi_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def like_multi_book_route(
    request_pydantic_model: social_p2p.LikeBookMapRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.LikeBookMapRequest = gateway.msg_from_dict_handle(
        social_pb2.LikeBookMapRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.like_multi_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_get_book_like_route(
    request_pydantic_model: social_p2p.GetBookLikesRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.GetBookLikesRequest = gateway.msg_from_dict_handle(
        social_pb2.GetBookLikesRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.get_book_like, "_loop", None):
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
    grpc_msg: social_pb2.GetBookLikesListResult = await stub.get_book_like(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def get_book_like_route(
    request_pydantic_model: social_p2p.GetBookLikesRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.GetBookLikesRequest = gateway.msg_from_dict_handle(
        social_pb2.GetBookLikesRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: social_pb2.GetBookLikesListResult = stub.get_book_like(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_get_book_like_other_route(
    request_pydantic_model: NestedGetBookLikesRequestGetBookLikeOtherRoute,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.NestedGetBookLikesRequest = gateway.msg_from_dict_handle(
        social_pb2.NestedGetBookLikesRequest, request_pydantic_model.dict(), ["nested"]
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.get_book_like_other, "_loop", None):
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
    grpc_msg: social_pb2.GetBookLikesListResult = await stub.get_book_like_other(
        request_msg, metadata=[("req_id", req_id)]
    )
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def get_book_like_other_route(
    request_pydantic_model: NestedGetBookLikesRequestGetBookLikeOtherRoute,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.NestedGetBookLikesRequest = gateway.msg_from_dict_handle(
        social_pb2.NestedGetBookLikesRequest, request_pydantic_model.dict(), ["nested"]
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: social_pb2.GetBookLikesListResult = stub.get_book_like_other(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_comment_book_route(
    request_pydantic_model: social_p2p.CommentBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.CommentBookRequest = gateway.msg_from_dict_handle(
        social_pb2.CommentBookRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.comment_book, "_loop", None):
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
    grpc_msg: Empty = await stub.comment_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def comment_book_route(
    request_pydantic_model: social_p2p.CommentBookRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.CommentBookRequest = gateway.msg_from_dict_handle(
        social_pb2.CommentBookRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: Empty = stub.comment_book(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


async def async_get_book_comment_route(
    request_pydantic_model: social_p2p.GetBookCommentRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.GetBookCommentRequest = gateway.msg_from_dict_handle(
        social_pb2.GetBookCommentRequest, request_pydantic_model.dict(), []
    )
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.BookSocial_stub.get_book_comment, "_loop", None):
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
    grpc_msg: social_pb2.GetBookCommentListResult = await stub.get_book_comment(
        request_msg, metadata=[("req_id", req_id)]
    )
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


def get_book_comment_route(
    request_pydantic_model: social_p2p.GetBookCommentRequest,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/book/social.proto_gateway"
    )
    stub: social_pb2_grpc.BookSocialStub = gateway.BookSocial_stub
    request_msg: social_pb2.GetBookCommentRequest = gateway.msg_from_dict_handle(
        social_pb2.GetBookCommentRequest, request_pydantic_model.dict(), []
    )
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: social_pb2.GetBookCommentListResult = stub.get_book_comment(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(grpc_msg, [], [])


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    BookSocial_stub: social_pb2_grpc.BookSocialStub
    stub_str_list: List[str] = ["BookSocial_stub"]

    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_example_proto_by_option/book/social.proto_gateway", self)
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []
        like_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_like_book_route = like_book_route_pait(feature_code="0")(async_like_book_route)
        pait_like_book_route = like_book_route_pait(feature_code="0")(like_book_route)
        like_multi_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_like_multi_book_route = like_multi_book_route_pait(feature_code="0")(async_like_multi_book_route)
        pait_like_multi_book_route = like_multi_book_route_pait(feature_code="0")(like_multi_book_route)
        get_book_like_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="test additional bindings",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionGetBookLikesListResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_like_route = get_book_like_route_pait(feature_code="0")(async_get_book_like_route)
        pait_get_book_like_route = get_book_like_route_pait(feature_code="0")(get_book_like_route)
        get_book_like_route_1_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Query,
            response_model_list=[BookSocialByOptionGetBookLikesListResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_like_route_1 = get_book_like_route_1_pait(feature_code="1")(async_get_book_like_route)
        pait_async_get_book_like_route_1.__name__ = "pait_async_get_book_like_route_1"
        pait_async_get_book_like_route_1.__qualname__ = pait_async_get_book_like_route_1.__qualname__.replace(
            "async_get_book_like_route", "pait_async_get_book_like_route_1"
        )
        pait_get_book_like_route_1 = get_book_like_route_1_pait(feature_code="1")(get_book_like_route)
        pait_get_book_like_route_1.__name__ = "pait_get_book_like_route_1"
        pait_get_book_like_route_1.__qualname__ = pait_get_book_like_route_1.__qualname__.replace(
            "get_book_like_route", "pait_get_book_like_route_1"
        )
        get_book_like_other_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionGetBookLikesListResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_like_other_route = get_book_like_other_route_pait(feature_code="0")(
            async_get_book_like_other_route
        )
        pait_get_book_like_other_route = get_book_like_other_route_pait(feature_code="0")(get_book_like_other_route)
        comment_book_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionEmptyJsonResponseModel] + response_model_list,
        )
        pait_async_comment_book_route = comment_book_route_pait(feature_code="0")(async_comment_book_route)
        pait_comment_book_route = comment_book_route_pait(feature_code="0")(comment_book_route)
        get_book_comment_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-book_social_by_option-BookSocial", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[BookSocialByOptionGetBookCommentListResultJsonResponseModel] + response_model_list,
        )
        pait_async_get_book_comment_route = get_book_comment_route_pait(feature_code="0")(async_get_book_comment_route)
        pait_get_book_comment_route = get_book_comment_route_pait(feature_code="0")(get_book_comment_route)
        self._add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/book_social_by_option-BookSocial/like_book",
                methods=["POST"],
                route=pait_async_like_book_route if self.is_async else pait_like_book_route,
            ),
            SimpleRoute(
                url="/book_social_by_option-BookSocial/like_multi_book",
                methods=["POST"],
                route=pait_async_like_multi_book_route if self.is_async else pait_like_multi_book_route,
            ),
            SimpleRoute(
                url="/book/get-book-like",
                methods=["POST"],
                route=pait_async_get_book_like_route if self.is_async else pait_get_book_like_route,
            ),
            SimpleRoute(
                url="/book_social_by_option-BookSocial/get_book_like",
                methods=["GET"],
                route=pait_async_get_book_like_route_1 if self.is_async else pait_get_book_like_route_1,
            ),
            SimpleRoute(
                url="/book/get-book-like-other",
                methods=["POST"],
                route=pait_async_get_book_like_other_route if self.is_async else pait_get_book_like_other_route,
            ),
            SimpleRoute(
                url="/book_social_by_option-BookSocial/comment_book",
                methods=["POST"],
                route=pait_async_comment_book_route if self.is_async else pait_comment_book_route,
            ),
            SimpleRoute(
                url="/book_social_by_option-BookSocial/get_book_comment",
                methods=["POST"],
                route=pait_async_get_book_comment_route if self.is_async else pait_get_book_comment_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
