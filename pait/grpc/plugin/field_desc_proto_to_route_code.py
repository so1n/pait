import logging
import sys
from textwrap import dedent
from typing import TYPE_CHECKING, List

from mypy_protobuf.main import Descriptors
from protobuf_to_pydantic.gen_code import BaseP2C
from protobuf_to_pydantic.gen_model import DescTemplate
from protobuf_to_pydantic.grpc_types import FileDescriptorProto

from pait import __version__
from pait.grpc.grpc_inspect import GrpcServiceOptionModel, get_grpc_service_model_from_option_message
from pait.grpc.plugin.model import GrpcModel
from pait.grpc.types import MethodDescriptorProto, ServiceDescriptorProto

if TYPE_CHECKING:
    from pait.grpc.plugin.config import ConfigModel

logger: logging.Logger = logging.getLogger(__name__)


class FileDescriptorProtoToRouteCode(BaseP2C):
    head_content: str = (
        "# This is an automatically generated file, please do not change\n"
        f"# gen by pait[{__version__}](https://github.com/so1n/pait)\n"
        "# type: ignore\n\n"
    )
    indent: int = 4
    attr_prefix: str = "gateway_attr"
    template_str: str = dedent(
        """
    def {func_name}(request_pydantic_model: {model_module_name}.{request_message_model}) -> Any:
        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_gateway")
        stub: {stub_module_name}.{service_name}Stub = pait_context.get().app_helper.get_attributes(
            "{attr_prefix}_{service_name}"
        )
        request_msg: {request_message} = gateway.get_msg_from_dict(
            {model_module_name}.{request_message_model}, request_pydantic_model.dict()
        )
        grpc_msg: {response_message} = stub.{method}(request_msg)
        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
    """
    )

    async_template_str: str = dedent(
        """
    async def {func_name}(request_pydantic_model: {model_module_name}.{request_message_model}) -> Any:
        gateway = pait_context.get().app_helper.get_attributes("{attr_prefix}_gateway")
        stub: {stub_module_name}.{service_name}Stub = pait_context.get().app_helper.get_attributes(
            "{attr_prefix}_{service_name}"
        )
        request_msg: {request_message} = gateway.get_msg_from_dict(
            {model_module_name}.{request_message_model}, request_pydantic_model.dict()
        )
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        if loop != stub.{method}._loop:  # type: ignore
            raise RuntimeError(
                "Loop is not same, "
                "the grpc channel must be initialized after the event loop of the api server is initialized"
            )
        else:
            grpc_msg: {response_message} = await stub.{method}(request_msg)
        return gateway.make_response(gateway.msg_to_dict(grpc_msg))
    """
    )

    response_template_str: str = dedent(
        """
        class {response_class_name}(JsonResponseModel):
            name: str = "{package}_{response_message_model}"
            description: str = {model_module_name}.{response_message_model}.__doc__ or ""
            response_data: Type[BaseModel] = {model_module_name}.{response_message_model}
    """
    )

    def __init__(self, fd: FileDescriptorProto, descriptors: Descriptors, config: "ConfigModel"):
        super().__init__(
            customer_import_set=config.customer_import_set,
            customer_deque=config.customer_deque,
            module_path=config.module_path,
            code_indent=config.code_indent,
        )
        self.config: "ConfigModel" = config
        self._add_import_code("pait.g", "pait_context")
        self._fd: FileDescriptorProto = fd
        self._descriptors: Descriptors = descriptors
        self._desc_template: DescTemplate = config.desc_template_instance

        self._parse_field_descriptor()

    def get_route_template(self, service: ServiceDescriptorProto, method: MethodDescriptorProto) -> str:
        """Can customize the template that generates the route according to different methods"""
        self._add_import_code("typing", "Callable")
        self._add_import_code("typing", "Any")
        if self.config.gateway_model == "sync":
            return self.template_str
        else:
            return self.async_template_str

    def _parse_field_descriptor(self) -> None:
        tab_str: str = self.indent * " "
        model_module_name = self._fd.name.split("/")[-1].replace(".proto", self.config.file_name_suffix)
        message_module_name = self._fd.name.split("/")[-1].replace(".proto", "_pb2")
        stub_module_name = self._fd.name.split("/")[-1].replace(".proto", "_pb2_grpc")
        self._add_import_code("pait", "field")
        self._add_import_code("pait.app.any", "add_multi_simple_route")
        self._add_import_code("pait.app.any", "SimpleRoute")
        self._add_import_code("pait.app.any", "set_app_attribute")
        self._add_import_code("pait.grpc.plugin.gateway", "BaseStaticGrpcGatewayRoute")
        self._add_import_code("pait.model.tag", "Tag")
        self._add_import_code("pait.model.response", "BaseResponseModel")
        self._add_import_code("pait.model.response", "JsonResponseModel")
        self._add_import_code("pydantic", "BaseModel")
        self._add_import_code("typing", "List")
        self._add_import_code("typing", "Type")

        self._add_import_code(".", model_module_name)
        self._add_import_code(".", message_module_name)
        self._add_import_code(".", stub_module_name)

        service_name_list: list = []
        grpc_model_list: List[GrpcModel] = []
        for service in self._fd.service:
            for method in service.method:
                func_name: str = f"{method.name}_route"
                service_name_list.append(service.name)
                service_model_list: List[GrpcServiceOptionModel] = []
                for field, option_message in method.options.ListFields():
                    if not field.full_name.endswith("api.http"):
                        continue
                    service_model_list.extend(get_grpc_service_model_from_option_message(option_message))
                input_type_name = method.input_type.split(".")[-1]
                output_type_name = method.output_type.split(".")[-1]
                if "Empty" in (input_type_name, output_type_name):
                    self._add_import_code("google.protobuf.empty_pb2", "Empty")
                template_dict = {
                    "attr_prefix": self.attr_prefix,
                    "method": method.name,
                    "func_name": func_name,
                    "request_message": f"{message_module_name}.{input_type_name}"
                    if input_type_name not in ("Empty",)
                    else input_type_name,
                    "response_message": f"{message_module_name}.{output_type_name}"
                    if output_type_name not in ("Empty",)
                    else output_type_name,
                    "request_message_model": input_type_name,
                    "response_message_model": output_type_name,
                    "service_name": service.name,
                    "model_module_name": model_module_name,
                    "message_module_name": message_module_name,
                    "stub_module_name": stub_module_name,
                    "package": self._fd.package,
                }
                grpc_method_url: str = f"/{self._fd.package}/{service.name}/{method.name}"
                if not service_model_list:
                    service_model_list.append(GrpcServiceOptionModel(url=grpc_method_url))
                for model_index, grpc_service_option_model in enumerate(service_model_list):
                    if not grpc_service_option_model.url:
                        grpc_service_option_model.url = grpc_method_url
                    grpc_model_list.append(
                        GrpcModel(
                            index=model_index,
                            func_name=func_name,
                            grpc_method_url=grpc_method_url,
                            template_dict=template_dict,
                            grpc_service_option_model=grpc_service_option_model,
                        )
                    )
                self._content_deque.append(self.get_route_template(service, method).format(**template_dict) + "\n\n")

        set_service_stub_str_list: List[str] = [
            f'set_app_attribute(self.app, "{self.attr_prefix}_{service_name}",'
            f" {stub_module_name}.{service_name}Stub(self.channel))"
            for service_name in set(service_name_list)
        ]
        simple_route_str_list: List[str] = []
        wrapper_route_str_list = []
        for grpc_model in grpc_model_list:
            grpc_service_option_model = grpc_model.grpc_service_option_model
            if not grpc_service_option_model.enable:
                continue
            group_list = grpc_service_option_model.group or grpc_service_option_model.url.split("/")[1]
            self._add_import_code("pait.model.tag", "Tag")
            tag_str_list: List[str] = [
                f'Tag("{tag}", "{desc}")'
                for tag, desc in grpc_model.grpc_service_option_model.tag
                + [("grpc" + "-" + grpc_model.grpc_method_url.split("/")[1].split(".")[0], "")]
            ]
            real_func_name: str = "pait_" + grpc_model.func_name
            if grpc_model.index:
                real_func_name = real_func_name + "_" + str(grpc_model.index)
            response_class_name: str = (
                grpc_model.template_dict["package"].title().replace("_", "")
                + grpc_model.template_dict["response_message_model"]
                + "JsonResponseModel"
            )
            grpc_model.template_dict["response_class_name"] = response_class_name
            response_class_str: str = self.response_template_str.format(**grpc_model.template_dict)
            response_class_str = response_class_str.replace(
                "{model_module_name}.{response_message_model}".format(**grpc_model.template_dict), "None"
            )
            self._content_deque.append(response_class_str + "\n")
            wrapper_route_str_list.append(
                f"{tab_str * 2}{real_func_name} = self._pait(\n"
                f'{tab_str * 3}name="{grpc_service_option_model.name}",\n'
                f"{tab_str * 3}group={self._get_value_code(group_list)},\n"
                f"{tab_str * 3}append_tag=({','.join(tag_str_list)},),\n"
                f'{tab_str * 3}desc="{grpc_service_option_model.desc}",\n'
                f'{tab_str * 3}summary="{grpc_service_option_model.summary}",\n'
                f"{tab_str * 3}default_field_class="
                f'{"field.Query" if grpc_service_option_model.http_method == "GET" else "field.Body"},\n'
                f"{tab_str * 3}response_model_list=[{response_class_name}] + response_model_list ,\n"
                f"{tab_str * 2})({grpc_model.func_name})"
            )
            if grpc_model.index:
                wrapper_route_str_list.append(
                    f'{tab_str * 2}{real_func_name}.__name__ = "{real_func_name}"\n'
                    f"{tab_str * 2}{real_func_name}.__qualname__ = "
                    f'{real_func_name}.__qualname__.replace("{grpc_model.func_name}", "{real_func_name}")'
                )
            simple_route_str_list.append(
                f"{tab_str * 3}SimpleRoute(\n"
                f'{tab_str * 4}url="{grpc_service_option_model.url}", \n'
                f'{tab_str * 4}methods=["{grpc_service_option_model.http_method}"], \n'
                f"{tab_str * 4}route={real_func_name}\n"
                f"{tab_str * 3})"
            )
        class_str: str = (
            "class StaticGrpcGatewayRoute(BaseStaticGrpcGatewayRoute):\n"
            f"{tab_str * 1}def gen_route(self) -> None:\n"
            f'{tab_str * 2}set_app_attribute(self.app, "{self.attr_prefix}_gateway", self)\n'
            f"{chr(10).join([tab_str * 2 + i for i in set_service_stub_str_list])}\n"
            f"{tab_str * 2}# The response model generated based on Protocol is important and needs to be put first\n"
            f"{tab_str * 2}response_model_list: List[Type[BaseResponseModel]] = self._pait._response_model_list or []\n"
            f"{chr(10).join(wrapper_route_str_list) if wrapper_route_str_list else ''}\n"
            f"{tab_str * 2}add_multi_simple_route(\n"
            f"{tab_str * 3}self.app,\n"
            f"{(',' + chr(10)).join(simple_route_str_list) + ',' if simple_route_str_list else ''}\n"
            f"{tab_str * 3}prefix=self.prefix,\n"
            f"{tab_str * 3}title=self.title,\n"
            f"{tab_str * 3}** self.kwargs\n"
            f"{tab_str * 2})\n"
        )
        logger.debug(class_str)
        print(class_str, file=sys.stderr)
        self._content_deque.append(class_str)
