import inspect
import json
import logging
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type

from google.protobuf.descriptor import MethodDescriptor, ServiceDescriptor  # type: ignore
from pydantic import BaseModel, Field

from pait.util.grpc_inspect.types import Message


class GrpcServiceModel(BaseModel):
    name: str = Field("")
    tag: List[Tuple[str, str]] = Field(default_factory=list)
    group: str = Field("")
    desc: str = Field("")
    summary: str = Field("")
    url: str = Field("")
    enable: bool = Field(True)
    http_method: str = Field("POST")


@dataclass()
class GrpcModel(object):
    invoke_name: str
    method: str
    alias_method: str
    grpc_service_model: GrpcServiceModel
    # func: Callable
    request: Type[Message] = Message
    response: Type[Message] = Message
    desc: str = ""


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

    def get_grpc_service_model_from_option_message(self, option_message: Message) -> List[GrpcServiceModel]:
        grpc_service_model_list: List[GrpcServiceModel] = []
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
                    grpc_service_model_list.extend(self.get_grpc_service_model_from_option_message(item))
            else:
                pait_dict[key] = value
        grpc_service_model: GrpcServiceModel = GrpcServiceModel(**pait_dict)
        grpc_service_model.http_method = grpc_service_model.http_method.upper()
        grpc_service_model_list.append(grpc_service_model)
        return grpc_service_model_list

    def get_service_by_message(
        self, input_message: Type[Message], out_message: Type[Message]
    ) -> List[GrpcServiceModel]:
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
                    for filed, option_message in method.GetOptions().ListFields():
                        if not filed.full_name.endswith("api.http"):
                            continue
                        return self.get_grpc_service_model_from_option_message(option_message)
        return []

    @staticmethod
    def get_pait_info_from_grpc_desc(desc: str, service_desc: str) -> GrpcServiceModel:
        pait_dict: dict = {}
        for line in service_desc.split("\n") + desc.split("\n"):
            line = line.strip()
            if not line.startswith("pait: {"):
                continue
            line = line.replace("pait:", "")
            pait_dict.update(json.loads(line))
        grpc_pait_model: GrpcServiceModel = GrpcServiceModel(**pait_dict)
        grpc_pait_model.http_method = grpc_pait_model.http_method.upper()
        return grpc_pait_model

    def _parse(self) -> None:
        line_list: List[str] = inspect.getsource(self._stub).split("\n")

        service_class_name: str = self._stub.__name__.replace("Stub", "Servicer")
        class_module: Optional[ModuleType] = inspect.getmodule(self._stub)
        if not class_module:
            raise RuntimeError(f"Can not found {self._stub} module")

        service_class: Type = getattr(class_module, service_class_name)

        for index, line in enumerate(line_list):
            if "self." not in line:
                continue
            if "channel.unary_unary" not in line:
                continue

            invoke_name: str = line.split("=")[0].replace("self.", "").strip()
            method: str = line_list[index + 1].strip()[1:-2]
            request: Type[Message] = self._gen_message(
                line_list[index + 2], r"request_serializer=(.+).SerializeToString", class_module
            )
            response: Type[Message] = self._gen_message(
                line_list[index + 3], r"response_deserializer=(.+).FromString", class_module
            )
            service_desc: str = service_class.__doc__ or ""
            desc: str = service_class.__dict__[invoke_name].__doc__ or ""
            grpc_service_model_list: List[GrpcServiceModel] = self.get_service_by_message(request, response)
            if not grpc_service_model_list:
                grpc_service_model_list = [self.get_pait_info_from_grpc_desc(desc, service_desc)]
            grpc_model_list: List[GrpcModel] = []
            for model_index, grpc_service_model in enumerate(grpc_service_model_list):
                if not grpc_service_model.url:
                    grpc_service_model.url = method
                grpc_model_list.append(
                    GrpcModel(
                        invoke_name=invoke_name,
                        method=method,
                        alias_method=method + str(model_index),
                        grpc_service_model=grpc_service_model,
                        desc=service_class.__dict__[invoke_name].__doc__ or "",
                        request=request,
                        response=response,
                    )
                )
            self._method_list_dict[method] = grpc_model_list
