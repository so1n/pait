import logging
from textwrap import dedent
from typing import List, Set, Type

from google.protobuf.any_pb2 import Any  # type: ignore
from protobuf_to_pydantic.gen_model import DescTemplate
from pydantic import confloat, conint
from pydantic.fields import FieldInfo

from pait.grpc.plugin.field_desc_proto_to_route_code import (
    FileDescriptorProtoToRouteCode as _FileDescriptorProtoToRouteCode,
)
from pait.grpc.types import MethodDescriptorProto, ServiceDescriptorProto

logging.basicConfig(format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.INFO)


class CustomerField(FieldInfo):
    pass


def customer_any() -> Any:
    return Any  # type: ignore


local_dict = {
    "CustomerField": CustomerField,
    "confloat": confloat,
    "conint": conint,
    "customer_any": customer_any,
}
comment_prefix = "pait"
desc_template: Type[DescTemplate] = DescTemplate
ignore_pkg_list: List[str] = ["validate", "p2p_validate", "pait.api"]
empty_type = dict


class FileDescriptorProtoToRouteCode(_FileDescriptorProtoToRouteCode):
    response_template_str: str = dedent(
        """
        class {response_class_name}(JsonResponseModel):
            class CustomerJsonResponseRespModel(BaseModel):
                code: int = Field(0, description="api code")
                msg: str = Field("success", description="api status msg")
                data: {model_module_name}.{response_message_model} = Field(description="api response data")

            name: str = "{package}_{response_message_model}"
            description: str = (
                {model_module_name}.{response_message_model}.__doc__ or ""
                 if {model_module_name}.{response_message_model}.__module__ != "builtins" else ""
            )
            response_data: Type[BaseModel] = CustomerJsonResponseRespModel
    """
    )

    def get_route_template(self, service: ServiceDescriptorProto, method: MethodDescriptorProto, is_async: bool) -> str:
        if service.name != "User":
            return super().get_route_template(service, method, is_async)
        if method.name in ("login_user", "create_user"):
            return super().get_route_template(service, method, is_async)
        self._add_import_code("pait.field", "Header")
        self._add_import_code("uuid", "uuid4")
        if method.name == "logout_user":
            if is_async:
                return dedent(
                    """
                    async def {func_name}(
                        request_pydantic_model: {model_module_name}.{request_message_model},
                        token: str = Header.i(description="User Token"),
                        req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                    ) -> Any:
                        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_{package}_gateway")
                        request_dict: dict = request_pydantic_model.dict()
                        request_dict["token"] = token
                        request_msg: {request_message} = gateway.get_msg_from_dict(
                            {message_module_name}.{request_message_model}, request_dict
                        )
                        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                        if loop != gateway.{stub_service_name}.{method}._loop:  # type: ignore
                            raise RuntimeError(
                                "Loop is not same, "
                                "the grpc channel must be initialized after the event loop"
                                "of the api server is initialized"
                            )
                        grpc_msg: {response_message} = await gateway.{stub_service_name}.{method}(
                            request_msg, metadata=[("req_id", req_id)]
                        )
                        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
                    """
                )
            else:
                return dedent(
                    """
                    def {func_name}(
                        request_pydantic_model: {model_module_name}.{request_message_model},
                        token: str = Header.i(description="User Token"),
                        req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                    ) -> Any:
                        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_{package}_gateway")
                        request_dict: dict = request_pydantic_model.dict()
                        request_dict["token"] = token
                        request_msg: {request_message} = gateway.get_msg_from_dict(
                            {message_module_name}.{request_message_model}, request_dict
                        )
                        grpc_msg: {response_message} = gateway.{stub_service_name}.{method}(
                            request_msg, metadata=[("req_id", req_id)]
                        )
                        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
                    """
                )
        else:
            if is_async:
                return dedent(
                    """
                    async def {func_name}(
                        request_pydantic_model: {model_module_name}.{request_message_model},
                        token: str = Header.i(description="User Token"),
                        req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                    ) -> Any:
                        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_{package}_gateway")
                        stub: {stub_module_name}.{service_name}Stub = gateway.{stub_service_name}
                        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                        if loop != stub.{method}._loop:  # type: ignore
                            raise RuntimeError(
                                "Loop is not same, "
                                "the grpc channel must be initialized after the event loop"
                                "of the api server is initialized"
                            )
                        # check token
                        result: {message_module_name}.GetUidByTokenResult = await stub.get_uid_by_token(
                            {message_module_name}.GetUidByTokenRequest(token=token)
                        )
                        if not result.uid:
                            raise RuntimeError("Not found user by token:" + token)
                        request_msg: {request_message} = gateway.get_msg_from_dict(
                            {message_module_name}.{request_message_model}, request_pydantic_model.dict()
                        )
                        grpc_msg: {response_message} = await stub.{method}(request_msg, metadata=[("req_id", req_id)])
                        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
                    """
                )
            else:
                return dedent(
                    """
                    def {func_name}(
                        request_pydantic_model: {model_module_name}.{request_message_model},
                        token: str = Header.i(description="User Token"),
                        req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                    ) -> Any:
                        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_{package}_gateway")
                        stub: {stub_module_name}.{service_name}Stub = gateway.{stub_service_name}
                        # check token
                        result: {message_module_name}.GetUidByTokenResult = stub.get_uid_by_token(
                            {message_module_name}.GetUidByTokenRequest(token=token)
                        )
                        if not result.uid:
                            raise RuntimeError("Not found user by token:" + token)
                        request_msg: {request_message} = gateway.get_msg_from_dict(
                            {message_module_name}.{request_message_model}, request_pydantic_model.dict()
                        )
                        grpc_msg: {response_message} = stub.{method}(request_msg, metadata=[("req_id", req_id)])
                        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
                    """
                )


customer_import_set: Set[str] = {"from pydantic import Field"}
file_descriptor_proto_to_route_code: Type[FileDescriptorProtoToRouteCode] = FileDescriptorProtoToRouteCode
