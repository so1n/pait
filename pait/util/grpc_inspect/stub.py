import inspect
import re
from dataclasses import dataclass
from pathlib import Path
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
    def __init__(self, stub: Any, parse_msg_desc: Optional[str] = None):
        self._stub: Any = stub
        self._parse_msg_desc: Optional[str] = parse_msg_desc
        self.name: str = self._stub.__name__
        self._method_dict: Dict[str, GrpcModel] = {}
        self._line_list: List[str] = inspect.getsource(stub).split("\n")

        class_module: Optional[ModuleType] = inspect.getmodule(stub)
        if not class_module:
            raise RuntimeError(f"Can not found {stub} module")
        self._class_module: ModuleType = class_module

        self._filename_desc_dict: Dict[str, Dict[str, Dict[str, str]]] = {}

        # self._gen_rpc_metadate()
        self._parse()

    @property
    def method_dict(self) -> Dict[str, GrpcModel]:
        return self._method_dict

    def _get_desc_from_pyi_file(self, filename: str) -> Dict[str, Dict[str, str]]:
        if filename in self._filename_desc_dict:
            return self._filename_desc_dict[filename]

        with open(filename, "r") as f:
            pyi_content: str = f.read()
        line_list = pyi_content.split("\n")

        _comment_model: bool = False
        _doc: str = ""
        _field_name: str = ""
        message_str: str = ""
        message_field_dict: Dict[str, Dict[str, str]] = {}
        for index, line in enumerate(line_list):
            if "class" in line:
                if line.endswith("google.protobuf.message.Message):"):
                    match_list = re.findall(r"class (.+)\(google.protobuf.message.Message", line)
                    if not match_list:
                        continue
                    message_str = match_list[0]
                else:
                    message_str = ""
                continue

            if message_str:
                line = line.strip()
                if _comment_model:
                    _doc += "\n" + line

                if not _comment_model and line.startswith('"""') and not line_list[index - 1].startswith("class"):
                    # start add doc
                    _field_name = line_list[index - 1].split(":")[0].strip()
                    _comment_model = True
                    _doc = line
                if (line.endswith('"""') or line == '"""') and _comment_model:
                    # end add doc
                    _comment_model = False
                    if message_str not in message_field_dict:
                        message_field_dict[message_str] = {}
                    message_field_dict[message_str][_field_name] = _doc.replace('"""', "")

        self._filename_desc_dict[filename] = message_field_dict
        return message_field_dict

    def _get_desc_from_proto_file(self, filename: str) -> Dict[str, Dict[str, str]]:
        if filename in self._filename_desc_dict:
            return self._filename_desc_dict[filename]

        with open(filename, "r") as f:
            protobuf_content: str = f.read()
        message_stack: List[str] = []
        message_field_dict: Dict[str, Dict[str, str]] = {}
        _field: str = ""
        _doc: str = ""
        _comment_model: bool = False

        for line in protobuf_content.split("\n"):
            _comment_model = False
            line_list: List[str] = line.split()
            for index, column in enumerate(line_list):
                if _comment_model:
                    _doc += column + " "
                    continue

                if column == "message" and line_list[index + 2] == "{":
                    # message parse start
                    message_stack.append(line_list[index + 1])
                    continue
                if message_stack:
                    if column == "}":
                        # message parse end
                        message_stack.pop()
                    elif column == "//":
                        # comment start
                        _comment_model = True
                        _doc += "\n"
                    elif column == "=":
                        # get field name
                        _field = line_list[index - 1]
                    elif column[-1] == ";":
                        # field parse end
                        if _doc:
                            message_str: str = message_stack[-1]
                            if message_str not in message_field_dict:
                                message_field_dict[message_str] = {}

                            message_field_dict[message_str][_field] = _doc
                        _field = ""
                        _doc = ""
        self._filename_desc_dict[filename] = message_field_dict
        return message_field_dict

    def _gen_message(self, line: str, match_str: str) -> Type[Message]:
        module_path: str = get_proto_msg_path(line, match_str)
        module_path_list: List[str] = module_path.split(".")
        message_module: ModuleType = getattr(self._class_module, module_path_list[0])
        message_model: Type[Message] = getattr(message_module, module_path_list[1])

        if not issubclass(message_model, Message):
            raise RuntimeError("Can not found message")

        if not self._parse_msg_desc:
            return message_model
        if Path(self._parse_msg_desc).exists():
            proto_file_name = message_model.DESCRIPTOR.file.name
            if proto_file_name.endswith("empty.proto"):
                return message_model
            file_str: str = self._parse_msg_desc
            if not file_str.endswith("/"):
                file_str += "/"
            message_field_dict: Dict[str, Dict[str, str]] = self._get_desc_from_proto_file(file_str + proto_file_name)
        elif self._parse_msg_desc == "by_mypy":
            pyi_file_name = inspect.getfile(message_module) + "i"
            if pyi_file_name.endswith("empty_pb2.pyi"):
                return message_model
            if not Path(pyi_file_name).exists():
                raise RuntimeError(f"Can not found {message_module} pyi file")
            message_field_dict = self._get_desc_from_pyi_file(pyi_file_name)
        elif self._parse_msg_desc == "by_pait":
            raise NotImplementedError("by_pait")
        else:
            raise ValueError(
                f"parse_msg_desc must be exist path or `by_mypy` or `by_pait`, not {self._parse_msg_desc})"
            )

        if message_model.__name__ in message_field_dict:
            message_model.__field_doc_dict__ = message_field_dict[message_model.__name__]
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
