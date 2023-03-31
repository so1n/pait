import logging
import sys
from typing import Type

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse
from mypy_protobuf.main import Descriptors, code_generation
from protobuf_to_pydantic.plugin.code_gen import CodeGen as _CodeGen
from protobuf_to_pydantic.plugin.code_gen import ConfigT

from pait.grpc.plugin.config import ConfigModel

# If want to parse option, need to import the corresponding file
#   see details:https://stackoverflow.com/a/59301849
from protobuf_to_pydantic.plugin.code_gen import p2p_validate_pb2  # isort:skip
from protobuf_to_pydantic.plugin.code_gen import validate_pb2  # isort:skip
from pait.grpc.proto import api_pb2  # isort:skip


logger = logging.getLogger(__name__)


class CodeGen(_CodeGen):
    def __init__(self) -> None:
        self.param_dict: dict = {}
        self.config_class: Type[ConfigT] = ConfigModel
        with code_generation() as (request, response):
            self.parse_param(request)
            self.gen_config()
            self.generate_pydantic_model(Descriptors(request), response)
            self.generate_route(Descriptors(request), response)

    def generate_route(self, descriptors: Descriptors, response: CodeGeneratorResponse) -> None:
        for name, fd in descriptors.to_generate.items():
            if fd.package in self.config.ignore_pkg_list:
                continue
            file = response.file.add()
            file.name = fd.name[:-6].replace("-", "_").replace(".", "/") + f"{self.config.route_file_name_suffix}.py"
            file.content = self.config.file_descriptor_proto_to_route_code(
                fd=fd, descriptors=descriptors, config=self.config
            ).content
            print(f"Writing route code to {file.name}", file=sys.stderr)
