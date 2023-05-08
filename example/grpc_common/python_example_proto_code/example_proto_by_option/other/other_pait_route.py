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
from pait.grpc import rebuild_message_type
from pait.grpc.plugin.gateway import BaseStaticGrpcGatewayRoute
from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.model.tag import Tag

from ..user import user_pb2, user_pb2_grpc
from . import other_p2p, other_pb2, other_pb2_grpc
from .other_p2p import NestedMessage as NestedMessageNestedDemoRoute

NestedMessageNestedDemoRoute = rebuild_message_type(  # type: ignore[misc]
    NestedMessageNestedDemoRoute,
    "nested_demo_route",
    exclude_column_name=[],
    nested=["map_demo", "${}", "repeated_demo", "$[]", "$.map_demo", "${}", "repeated_demo"],
)


class OtherSocialByOptionNestedMessageJsonResponseModel(JsonResponseModel):
    class CustomerJsonResponseRespModel(BaseModel):
        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: NestedMessageNestedDemoRoute = Field(description="api response data")

    name: str = "other_social_by_option_NestedMessageNestedDemoRoute"
    description: str = (
        NestedMessageNestedDemoRoute.__doc__ or "" if NestedMessageNestedDemoRoute.__module__ != "builtins" else ""
    )
    response_data: Type[BaseModel] = CustomerJsonResponseRespModel


async def async_nested_demo_route(
    request_pydantic_model: Empty,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/other/other.proto_gateway"
    )
    stub: other_pb2_grpc.OtherStub = gateway.Other_stub
    request_msg: Empty = gateway.msg_from_dict_handle(Empty, request_pydantic_model.dict(), [])
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop != getattr(gateway.Other_stub.nested_demo, "_loop", None):
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
    grpc_msg: other_pb2.NestedMessage = await stub.nested_demo(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(
        grpc_msg, [], ["$.map_demo", "$[]", "${}", "${}", "map_demo", "repeated_demo", "repeated_demo"]
    )


def nested_demo_route(
    request_pydantic_model: Empty,
    token: str = Header.i(description="User Token"),
    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
) -> Any:
    gateway: "StaticGrpcGatewayRoute" = pait_context.get().app_helper.get_attributes(
        "gateway_attr_example_proto_by_option/other/other.proto_gateway"
    )
    stub: other_pb2_grpc.OtherStub = gateway.Other_stub
    request_msg: Empty = gateway.msg_from_dict_handle(Empty, request_pydantic_model.dict(), [])
    # check token
    result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
        user_pb2.GetUidByTokenRequest(token=token)
    )
    if not result.uid:
        raise RuntimeError("Not found user by token:" + token)
    grpc_msg: other_pb2.NestedMessage = stub.nested_demo(request_msg, metadata=[("req_id", req_id)])
    return gateway.msg_to_dict_handle(
        grpc_msg, [], ["$.map_demo", "$[]", "${}", "${}", "map_demo", "repeated_demo", "repeated_demo"]
    )


class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):
    Other_stub: other_pb2_grpc.OtherStub
    stub_str_list: List[str] = ["Other_stub"]

    def gen_route(self) -> None:
        set_app_attribute(self.app, "gateway_attr_example_proto_by_option/other/other.proto_gateway", self)
        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []
        nested_demo_route_pait: Pait = self._pait.create_sub_pait(
            author=(),
            name="",
            group="",
            append_tag=(
                Tag("grpc-other_social_by_option-Other", ""),
                self._grpc_tag,
            ),
            desc="",
            summary="",
            default_field_class=field.Body,
            response_model_list=[OtherSocialByOptionNestedMessageJsonResponseModel] + response_model_list,
        )
        pait_async_nested_demo_route = nested_demo_route_pait(feature_code="0")(async_nested_demo_route)
        pait_nested_demo_route = nested_demo_route_pait(feature_code="0")(nested_demo_route)
        self._add_multi_simple_route(
            self.app,
            SimpleRoute(
                url="/other/nested-demo",
                methods=["POST"],
                route=pait_async_nested_demo_route if self.is_async else pait_nested_demo_route,
            ),
            prefix=self.prefix,
            title=self.title,
            **self.kwargs,
        )
