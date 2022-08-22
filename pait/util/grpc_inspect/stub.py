import inspect
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Dict, List, Optional, Type

from pait.util.grpc_inspect.types import Message


def get_proto_msg_path(line: str, re_str: str) -> str:
    module_path_find_list = re.findall(re_str, line)
    if len(module_path_find_list) != 1:
        raise ValueError("module path not found")
    return module_path_find_list[0]


@dataclass()
class GrpcModel(object):
    invoke_name: str
    method: str
    # func: Callable
    request: Type[Message] = Message
    response: Type[Message] = Message
    desc: str = ""
    service_desc: str = ""


class ParseStub(object):
    def __init__(self, stub: Any):
        self._stub: Any = stub
        self.name: str = self._stub.__name__
        self._method_dict: Dict[str, GrpcModel] = {}
        self._line_list: List[str] = inspect.getsource(stub).split("\n")

        class_module: Optional[ModuleType] = inspect.getmodule(stub)
        if not class_module:
            raise RuntimeError(f"Can not found {stub} module")
        self._class_module: ModuleType = class_module

        self._filename_desc_dict: Dict[str, Dict[str, Dict[str, str]]] = {}

        self._parse()

    @property
    def method_dict(self) -> Dict[str, GrpcModel]:
        return self._method_dict

    def _gen_message(self, line: str, match_str: str) -> Type[Message]:
        module_path: str = get_proto_msg_path(line, match_str)
        module_path_list: List[str] = module_path.split(".")
        message_module: ModuleType = getattr(self._class_module, module_path_list[0])
        message_model: Type[Message] = getattr(message_module, module_path_list[1])
        setattr(message_model, "_message_module", message_module)

        if not issubclass(message_model, Message):
            raise RuntimeError("Can not found message")

        return message_model

    def _parse(self) -> None:
        line_list: List[str] = self._line_list

        service_class_name: str = self._stub.__name__.replace("Stub", "Servicer")
        service_class: Type = getattr(self._class_module, service_class_name)

        for index, line in enumerate(line_list):
            if "self." not in line:
                continue
            if "channel.unary_unary" not in line:
                continue

            invoke_name: str = line.split("=")[0].replace("self.", "").strip()
            method: str = line_list[index + 1].strip()[1:-2]
            request: Type[Message] = self._gen_message(
                line_list[index + 2], r"request_serializer=(.+).SerializeToString"
            )
            response: Type[Message] = self._gen_message(line_list[index + 3], r"response_deserializer=(.+).FromString")
            self._method_dict[method] = GrpcModel(
                invoke_name=invoke_name,
                method=method,
                desc=service_class.__dict__[invoke_name].__doc__ or "",
                service_desc=service_class.__doc__ or "",
                request=request,
                response=response,
            )
