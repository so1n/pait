import inspect
import json
import logging
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from google.protobuf.descriptor import MethodDescriptor, ServiceDescriptor  # type: ignore
from google.protobuf.json_format import MessageToDict  # type: ignore
from pydantic import BaseModel, Field, validator

from pait.grpc.types import Message

__all__ = [
    "BuildMessageModel",
    "GrpcServiceOptionModel",
    "GrpcModel",
    "get_grpc_service_model_from_option_message",
    "ParseStub",
]


class BuildMessageModel(BaseModel):
    exclude_column_name: list = Field(default_factory=list)
    nested: list = Field(default_factory=list)

    @validator("exclude_column_name", pre=True)
    def exclude_column_name_validator(cls, v: Union[str, list]) -> list:
        if isinstance(v, str):
            return [i for i in v.split(",") if i]
        return v

    @validator("nested", pre=True)
    def nested_validator(cls, v: Union[str, list]) -> list:
        if isinstance(v, str):
            return [i for i in v.split("/") if i]
        return v


class RequestBuildMessageModel(BuildMessageModel):
    @validator("nested", pre=True)
    def nested_validator(cls, v: Union[str, list]) -> list:
        if isinstance(v, str):
            return [i for i in v.split("/") if i if not i.startswith("$")]
        return v


class GrpcServiceOptionModel(BaseModel):
    """grpc service option"""

    name: str = Field("", description="service name")
    author: Tuple[str] = Field(default_factory=tuple, description="service author")
    tag: List[Tuple[str, str]] = Field(default_factory=list, description="service openapi tag")
    group: str = Field("", description="service pait group")
    desc: str = Field("", description="service openapi description")
    summary: str = Field("", description="service openapi summary")
    url: str = Field("", description="service url")
    enable: bool = Field(True, description="Whether to enable this service")
    http_method: str = Field("POST")
    request_message: RequestBuildMessageModel = Field(
        default_factory=RequestBuildMessageModel, description="request message"
    )
    response_message: BuildMessageModel = Field(default_factory=BuildMessageModel, description="response message")


@dataclass()
class GrpcModel(object):
    invoke_name: str
    grpc_method_url: str
    alias_grpc_method_url: str
    grpc_service_option_model: GrpcServiceOptionModel
    # func: Callable
    request: Type[Message] = Message
    response: Type[Message] = Message
    desc: str = ""


def get_grpc_service_model_from_option_message(option_message: Message) -> List[GrpcServiceOptionModel]:
    grpc_service_model_list: List[GrpcServiceOptionModel] = []
    pait_dict: dict = {}
    for rule_filed, value in option_message.ListFields():
        key: str = rule_filed.name
        if key == "tag":
            pait_dict[key] = [(tag.name, tag.desc) for tag in value]
        elif key == "not_enable":
            pait_dict["enable"] = not value
        elif rule_filed.containing_oneof:
            if value.url:
                pait_dict["url"] = value.url
            if key == "custom":
                logging.warning(f"Not support column:{key}")
            elif key != "any":
                pait_dict["http_method"] = key
        elif key in ("body", "response_body"):
            logging.warning(f"Not support column:{key}")
        elif key == "additional_bindings":
            for item in value:
                grpc_service_model_list.extend(get_grpc_service_model_from_option_message(item))
        elif key in ("request_message", "response_message"):
            if isinstance(value, dict):
                pait_dict[key] = value
            else:
                pait_dict[key] = MessageToDict(value, preserving_proto_field_name=True)
        else:
            pait_dict[key] = value

    grpc_service_model: GrpcServiceOptionModel = GrpcServiceOptionModel(**pait_dict)
    grpc_service_model.http_method = grpc_service_model.http_method.upper()
    grpc_service_model_list.append(grpc_service_model)
    return grpc_service_model_list


class ParseStub(object):
    def __init__(self, stub: Any):
        self._stub: Any = stub
        self.name: str = self._stub.__name__
        self._method_list_dict: Dict[str, List[GrpcModel]] = {}
        self._filename_desc_dict: Dict[str, Dict[str, Dict[str, str]]] = {}

        self._parse()

    @property
    def method_list_dict(self) -> Dict[str, List[GrpcModel]]:
        return self._method_list_dict

    @staticmethod
    def _gen_message(line: str, match_str: str, class_module: ModuleType) -> Type[Message]:
        module_path_find_list = re.findall(match_str, line)
        if len(module_path_find_list) != 1:
            raise ValueError("module path not found")
        module_path: str = module_path_find_list[0]
        module_path_list: List[str] = module_path.split(".")
        message_module: ModuleType = getattr(class_module, module_path_list[0])
        message_model: Type[Message] = getattr(message_module, module_path_list[1])
        setattr(message_model, "_message_module", message_module)

        if not issubclass(message_model, Message):
            raise RuntimeError("Can not found message")

        return message_model

    def get_service_option_from_message(
        self, input_message: Type[Message], out_message: Type[Message]
    ) -> List[GrpcServiceOptionModel]:
        for message in [input_message, out_message]:
            message_module: ModuleType = getattr(message, "_message_module")
            server_list: List[ServiceDescriptor] = message_module.DESCRIPTOR.services_by_name.values()  # type: ignore
            for server_descriptor in server_list:
                for method in server_descriptor.methods:
                    if not (
                        method.input_type.full_name == input_message.DESCRIPTOR.full_name
                        and method.output_type.full_name == out_message.DESCRIPTOR.full_name
                    ):
                        continue
                    if not method.GetOptions().ListFields():
                        continue
                    for field, option_message in method.GetOptions().ListFields():
                        if not field.full_name.endswith("api.http"):
                            continue
                        return get_grpc_service_model_from_option_message(option_message)
        return []

    @staticmethod
    def get_service_option_from_grpc_desc(desc: str, service_desc: str) -> List[GrpcServiceOptionModel]:
        grpc_pait_model_list: List[GrpcServiceOptionModel] = []
        pait_dict: dict = {}
        for line in service_desc.split("\n") + desc.split("\n"):
            line = line.strip()
            if not line.startswith("pait: {"):
                continue
            line = line.replace("pait:", "")
            pait_dict.update(json.loads(line))

        while True:
            grpc_pait_model: GrpcServiceOptionModel = GrpcServiceOptionModel(**pait_dict)
            grpc_pait_model.http_method = grpc_pait_model.http_method.upper()
            grpc_pait_model_list.append(grpc_pait_model)
            pait_dict = pait_dict.pop("additional_bindings", None)
            if not pait_dict:
                break

        return grpc_pait_model_list

    def _parse(self) -> None:
        # get stub source code
        line_list: List[str] = inspect.getsource(self._stub).split("\n")

        # get grpc service
        service_class_name: str = self._stub.__name__.replace("Stub", "Servicer")
        class_module: Optional[ModuleType] = inspect.getmodule(self._stub)
        if not class_module:
            raise RuntimeError(f"Can not found {self._stub} module")
        service_class: Type = getattr(class_module, service_class_name)

        # parse source code
        for index, line in enumerate(line_list):
            # Only need to get the function signature (currently only support 'unary_unary')
            if "self." not in line:
                continue
            if "channel.unary_unary" not in line:
                continue

            invoke_name: str = line.split("=")[0].replace("self.", "").strip()
            # The next line of the calling method must be the URL of the gRPC method
            grpc_method_url: str = line_list[index + 1].strip()[1:-2]
            request: Type[Message] = self._gen_message(
                line_list[index + 2], r"request_serializer=(.+).SerializeToString", class_module
            )
            response: Type[Message] = self._gen_message(
                line_list[index + 3], r"response_deserializer=(.+).FromString", class_module
            )
            service_desc: str = service_class.__doc__ or ""
            desc: str = service_class.__dict__[invoke_name].__doc__ or ""

            # Get the Option for each method in the gRPC Service through protocol optional
            grpc_service_option_model_list: List[GrpcServiceOptionModel] = self.get_service_option_from_message(
                request, response
            )
            if not grpc_service_option_model_list:
                # Get the Option for each method in the gRPC Service through comment
                grpc_service_option_model_list = self.get_service_option_from_grpc_desc(desc, service_desc)
            grpc_model_list: List[GrpcModel] = []
            for model_index, grpc_service_option_model in enumerate(grpc_service_option_model_list):
                if not grpc_service_option_model.url:
                    grpc_service_option_model.url = grpc_method_url
                grpc_model_list.append(
                    GrpcModel(
                        invoke_name=invoke_name,
                        grpc_method_url=grpc_method_url,
                        alias_grpc_method_url=grpc_method_url + str(model_index),
                        grpc_service_option_model=grpc_service_option_model,
                        desc=desc,
                        request=request,
                        response=response,
                    )
                )
            self._method_list_dict[grpc_method_url] = grpc_model_list
