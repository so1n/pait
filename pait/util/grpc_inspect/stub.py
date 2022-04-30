import inspect
import re
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional, Type

from google.protobuf.message import Message  # type: ignore


def get_proto_msg_path(line: str, re_str: str) -> str:
    module_path_find_list = re.findall(re_str, line)
    if len(module_path_find_list) != 1:
        raise ValueError("module path not found")
    return module_path_find_list[0]


@dataclass()
class GrpcModel(object):
    method: str
    func: Callable
    request: Type[Message] = Message
    response: Type[Message] = Message


class ParseStub(object):
    def __init__(self, stub: Any):
        self._stub: Any = stub
        self._method_dict: Dict[str, GrpcModel] = {}

        grpc_invoke_dict: Dict[str, Callable] = self._stub.__dict__.copy()
        for value in grpc_invoke_dict.values():
            if hasattr(value, "__wrapped__"):
                value = value.__wrapped__  # type: ignore
            method = value._method  # type: ignore
            if isinstance(method, bytes):
                method = method.decode()
            self._method_dict[method] = GrpcModel(method=method, func=value)

        self._line_list: List[str] = inspect.getsource(stub.__class__).split("\n")
        class_module: Optional[ModuleType] = inspect.getmodule(stub.__class__)
        if not class_module:
            raise RuntimeError(f"Can not found {stub} module")

        self._class_module: ModuleType = class_module
        self._sys_module_dict = sys.modules[stub.__class__.__module__].__dict__
        self._parse()

    @property
    def method_dict(self) -> Dict[str, GrpcModel]:
        return self._method_dict

    def _parse(self) -> None:
        method_dict_iter: Iterable = iter(self._method_dict.items())
        line_list: List[str] = self._line_list
        for index, line in enumerate(line_list):
            if "self." not in line:
                continue
            try:
                method_name, grpc_model = next(method_dict_iter)  # type: ignore
            except StopIteration:
                continue

            print(method_name)
            if method_name.split("/")[-1] not in line and method_name not in line_list[index + 1]:
                continue

            request_line: str = line_list[index + 2]
            response_line: str = line_list[index + 3]

            request_module_path: str = get_proto_msg_path(request_line, r"request_serializer=(.+).SerializeToString")
            response_module_path: str = get_proto_msg_path(response_line, r"response_deserializer=(.+).FromString")
            request_module: ModuleType = self._class_module
            for module_path in request_module_path.split("."):
                request_module = getattr(request_module, module_path)
            response_module: ModuleType = self._class_module
            for module_path in response_module_path.split("."):
                response_module = getattr(response_module, module_path)
            grpc_model.request = request_module
            grpc_model.response = response_module
