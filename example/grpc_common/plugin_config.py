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


class FileDescriptorProtoToRouteCode(_FileDescriptorProtoToRouteCode):
    response_template_str: str = dedent(
        """
        class {response_class_name}(JsonResponseModel):
            class CustomerJsonResponseRespModel(BaseModel):
                code: int = Field(0, description="api code")
                msg: str = Field("success", description="api status msg")
                data: {model_module_name}.{response_message_model} = Field(description="api response data")

            name: str = "{package}_{response_message_model}"
            description: str = {model_module_name}.{response_message_model}.__doc__ or ""
            response_data: Type[BaseModel] = CustomerJsonResponseRespModel
    """
    )


customer_import_set: Set[str] = {"from pydantic import Field"}
file_descriptor_proto_to_route_code: Type[FileDescriptorProtoToRouteCode] = FileDescriptorProtoToRouteCode
