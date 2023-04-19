import logging
from textwrap import dedent
from typing import List, Set, Type

from google.protobuf.any_pb2 import Any  # type: ignore
from jinja2 import Template
from pydantic import confloat, conint
from pydantic.fields import FieldInfo

from pait.grpc.plugin.field_desc_proto_to_route_code import (
    FileDescriptorProtoToRouteCode as _FileDescriptorProtoToRouteCode,
)
from pait.grpc.plugin.field_desc_proto_to_route_code import GrpcModel

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
# desc_template: Type[DescTemplate] = DescTemplate
ignore_pkg_list: List[str] = ["validate", "p2p_validate", "pait.api"]
empty_type = dict


class FileDescriptorProtoToRouteCode(_FileDescriptorProtoToRouteCode):
    response_jinja_template_str: str = dedent(
        """
        class {{response_class_name}}(JsonResponseModel):
            class CustomerJsonResponseRespModel(BaseModel):
                code: int = Field(0, description="api code")
                msg: str = Field("success", description="api status msg")
                {% if response_message_model_name == "Empty" %}
                data: {{gen_code._get_value_code(gen_code.config.empty_type)}} = Field(description="api response data")
                {% else %}
                data: {{response_message_model_name}} = Field(description="api response data")
                {% endif %}

            name: str = "{{package}}_{{response_message_model_name}}"
            {% if response_message_model_name == "Empty" %}
            description: str = (
                {{gen_code._get_value_code(gen_code.config.empty_type)}}.__doc__ or ""
                if {{gen_code._get_value_code(gen_code.config.empty_type)}}.__module__ != "builtins" else ""
            )
            {% else %}
            description: str = (
                {{response_message_model_name}}.__doc__ or ""
                if {{response_message_model_name}}.__module__ != "builtins" else ""
            )
            {% endif %}
            response_data: Type[BaseModel] = CustomerJsonResponseRespModel
    """
    )

    def get_route_code(self, grpc_model: GrpcModel, template_dict: dict) -> str:
        if grpc_model.grpc_descriptor_method.name in ("login_user", "create_user"):
            return super().get_route_code(grpc_model, template_dict)

        self._add_import_code("pait.field", "Header")
        self._add_import_code("uuid", "uuid4")
        if grpc_model.grpc_descriptor_method.name == "logout_user":
            route_func_jinja_template_str: str = dedent(
                """
            {{ 'async def' if is_async else 'def' }} {{func_name}}(
                request_pydantic_model: {{request_message_model_name}},
                token: str = Header.i(description="User Token"),
                req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
            ) -> Any:
                gateway: "{{gateway_name}}" = pait_context.get().app_helper.get_attributes(
                    "{{attr_prefix}}_{{filename}}_gateway"
                )
                request_dict: dict = request_pydantic_model.dict()
                request_dict["token"] = token
                request_msg: {{request_message_name}} = gateway.msg_from_dict_handle(
                    {{request_message_name}},
                    request_dict,
                    {{gen_code._get_value_code(grpc_service_option_model.request_message.nested)}}
                )
            {% if is_async %}
                loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                if loop != getattr(gateway.{{stub_service_name}}.{{method}}, "_loop", None):
                    raise RuntimeError(
                        "Loop is not same, "
                        "the grpc channel must be initialized after the event loop of the api server is initialized"
                    )
                else:
                    grpc_msg: {{response_message_name}} = await gateway.{{stub_service_name}}.{{method}}(
                        request_msg, metadata=[("req_id", req_id)])
            {% else %}
                grpc_msg: {{response_message_name}} = gateway.{{stub_service_name}}.{{method}}(
                    request_msg, metadata=[("req_id", req_id)])
            {% endif %}
                return gateway.msg_to_dict_handle(
                    grpc_msg,
                    {{gen_code._get_value_code(grpc_service_option_model.response_message.exclude_column_name)}},
                    {{gen_code._get_value_code(grpc_service_option_model.response_message.nested)}}
                )
                """
            )
        else:
            route_func_jinja_template_str = dedent(
                """
            {{ 'async def' if is_async else 'def' }} {{func_name}}(
                request_pydantic_model: {{request_message_model_name}},
                token: str = Header.i(description="User Token"),
                req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
            ) -> Any:
                gateway: "{{gateway_name}}" = pait_context.get().app_helper.get_attributes(
                    "{{attr_prefix}}_{{filename}}_gateway"
                )
                stub: {{stub_module_name}}.{{service_name}}Stub = gateway.{{stub_service_name}}
                request_msg: {{request_message_name}} = gateway.msg_from_dict_handle(
                    {{request_message_name}},
                    request_pydantic_model.dict(),
                    {{gen_code._get_value_code(grpc_service_option_model.request_message.nested)}}
                )
            {% if is_async %}
                loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
                if loop != getattr(gateway.{{stub_service_name}}.{{method}}, "_loop", None):
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
                grpc_msg: {{response_message_name}} = await stub.{{method}}(
                    request_msg, metadata=[("req_id", req_id)]
                )
            {% else %}
                # check token
                result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(gateway.channel).get_uid_by_token(
                    user_pb2.GetUidByTokenRequest(token=token)
                )
                if not result.uid:
                    raise RuntimeError("Not found user by token:" + token)
                grpc_msg: {{response_message_name}} = stub.{{method}}(request_msg, metadata=[("req_id", req_id)])
            {% endif %}
                return gateway.msg_to_dict_handle(
                    grpc_msg,
                    {{gen_code._get_value_code(grpc_service_option_model.response_message.exclude_column_name)}},
                    {{gen_code._get_value_code(grpc_service_option_model.response_message.nested)}}
                )
            """
            )
        return Template(route_func_jinja_template_str, trim_blocks=True, lstrip_blocks=True).render(**template_dict)

    def _parse_field_descriptor(self) -> None:
        self._add_import_code("..user", "user_pb2")
        self._add_import_code("..user", "user_pb2_grpc")
        super()._parse_field_descriptor()


customer_import_set: Set[str] = {"from pydantic import Field"}
file_descriptor_proto_to_route_code: Type[FileDescriptorProtoToRouteCode] = FileDescriptorProtoToRouteCode
