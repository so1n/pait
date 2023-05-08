import logging
from dataclasses import asdict
from textwrap import dedent
from typing import TYPE_CHECKING, List

from jinja2 import Template
from mypy_protobuf.main import Descriptors
from protobuf_to_pydantic.gen_code import BaseP2C
from protobuf_to_pydantic.gen_model import DescTemplate
from protobuf_to_pydantic.grpc_types import FileDescriptorProto

from pait.__version__ import __version__
from pait.grpc import GrpcServiceOptionModel, get_grpc_service_model_from_option_message
from pait.grpc.plugin.model import GrpcModel

if TYPE_CHECKING:
    from pait.grpc.plugin.config import ConfigModel

logger: logging.Logger = logging.getLogger(__name__)


class FileDescriptorProtoToRouteCode(BaseP2C):
    head_content: str = (
        "# This is an automatically generated file, please do not change\n"
        f"# gen by pait[{__version__}](https://github.com/so1n/pait)\n"
    )
    indent: int = 4
    attr_prefix: str = "gateway_attr"
    gateway_name: str = "StaticGrpcGatewayRoute"
    route_func_jinja_template_str: str = dedent(
        """
    {% if  request_message_model in ("Empty",) %}
    {{ 'async def' if is_async else 'def' }} {{func_name}}() -> Any:
    {% else %}
    {{ 'async def' if is_async else 'def' }} {{func_name}}(
        request_pydantic_model: {{request_message_model_name}}
    ) -> Any:
    {% endif %}
        gateway: "{{gateway_name}}" = pait_context.get().app_helper.get_attributes(
            "{{attr_prefix}}_{{filename}}_gateway"
        )
    {% if  request_message_model in ("Empty", ) %}
        request_msg: {{request_message_name}} = {{request_message_name}}()
    {% else %}
        request_msg: {{request_message_name}} = gateway.msg_from_dict_handle(
            {{request_message_name}},
            request_pydantic_model.dict(),
            {{gen_code._get_value_code(grpc_service_option_model.request_message.nested)}}
        )
    {% endif %}
    {% if is_async %}
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        if loop != getattr(gateway.{{stub_service_name}}.{{method}}, "_loop", None):
            raise RuntimeError(
                "Loop is not same, "
                "the grpc channel must be initialized after the event loop of the api server is initialized"
            )
        else:
            grpc_msg: {{response_message_name}} = await gateway.{{stub_service_name}}.{{method}}(
                request_msg
            )
    {% else %}
        grpc_msg: {{response_message_name}} = gateway.{{stub_service_name}}.{{method}}(request_msg)
    {% endif %}
        return gateway.msg_to_dict_handle(
            grpc_msg,
            {{gen_code._get_value_code(grpc_service_option_model.response_message.exclude_column_name)}},
            {{gen_code._get_value_code(grpc_service_option_model.response_message.nested)}}
        )
        """
    )

    response_jinja_template_str: str = dedent(
        """
    class {{response_class_name}}(JsonResponseModel):
        name: str = "{{package}}_{{response_message_model_name}}"
        {% if response_message_model_name == "Empty" %}
        description: str = (
            {{gen_code._get_value_code(gen_code.config.empty_type)}}.__doc__ or ""
            if {{gen_code._get_value_code(gen_code.config.empty_type)}}.__module__ != "builtins" else ""
        )
        response_data: {{
            gen_code._get_value_code(gen_code.config.empty_type)
        }} = {{gen_code._get_value_code(gen_code.config.empty_type)}}
        {% else %}
        description: str = (
            {{response_message_model_name}}.__doc__ or ""
            if {{response_message_model_name}}.__module__ != "builtins" else ""
        )
        response_data: Type[BaseModel] = {{response_message_model_name}}
        {% endif %}
    """
    )

    def __init__(self, fd: FileDescriptorProto, descriptors: Descriptors, config: "ConfigModel"):
        config = config.copy(deep=True)
        super().__init__(
            customer_import_set=config.customer_import_set,
            customer_deque=config.customer_deque,
            module_path=config.module_path,
            code_indent=config.code_indent,
        )
        self.config: "ConfigModel" = config
        self._fd: FileDescriptorProto = fd
        self._descriptors: Descriptors = descriptors
        self._desc_template: DescTemplate = config.desc_template_instance

        self._parse_field_descriptor()

    def get_route_code(self, grpc_model: GrpcModel, template_dict: dict) -> str:
        """Can customize the template that generates the route according to different methods"""
        return Template(self.route_func_jinja_template_str, trim_blocks=True, lstrip_blocks=True).render(
            **template_dict
        )

    def get_response_code(self, grpc_model: GrpcModel, template_dict: dict) -> str:
        """Can customize the template that generates the response according to different methods"""
        response_class_str: str = Template(
            self.response_jinja_template_str, trim_blocks=True, lstrip_blocks=True
        ).render(**template_dict)
        return response_class_str

    def get_pait_code(self, tab_str: str, pait_name: str, grpc_model: GrpcModel) -> str:
        # can't change tab_str, pait_name value
        tag_str_list: List[str] = [
            f'Tag("{tag}", "{desc}")'
            for tag, desc in grpc_model.grpc_service_option_model.tag
            + [("grpc" + "-" + grpc_model.grpc_method_url.split("/")[1].split(".")[0], "")]
        ]
        tag_str_list.append("self._grpc_tag")
        return (
            f"{tab_str * 2}{pait_name}: Pait = self._pait.create_sub_pait(\n"
            f"{tab_str * 3}author={self._get_value_code(grpc_model.grpc_service_option_model.author, sort=False)},\n"
            f'{tab_str * 3}name="{grpc_model.grpc_service_option_model.name}",\n'
            f"{tab_str * 3}group={self._get_value_code(grpc_model.grpc_service_option_model.group, sort=False)},\n"
            f"{tab_str * 3}append_tag=({','.join(tag_str_list)},),\n"
            f'{tab_str * 3}desc="{grpc_model.grpc_service_option_model.desc}",\n'
            f'{tab_str * 3}summary="{grpc_model.grpc_service_option_model.summary}",\n'
            f"{tab_str * 3}default_field_class="
            f'{"field.Query" if grpc_model.grpc_service_option_model.http_method == "GET" else "field.Body"},\n'
            f"{tab_str * 3}response_model_list=[{grpc_model.response_class_name}] + response_model_list ,\n"
            f"{tab_str * 2})"
        )

    def _parse_field_descriptor(self) -> None:
        tab_str: str = self.indent * " "
        model_module_name = self._fd.name.split("/")[-1].replace(".proto", self.config.file_name_suffix)
        message_module_name = self._fd.name.split("/")[-1].replace(".proto", "_pb2")
        stub_module_name = self._fd.name.split("/")[-1].replace(".proto", "_pb2_grpc")

        self._add_import_code("asyncio")
        self._add_import_code("pait", "field")
        self._add_import_code("pait.app.any", "SimpleRoute")
        self._add_import_code("pait.app.any", "set_app_attribute")
        self._add_import_code("pait.core", "Pait")
        self._add_import_code("pait.g", "pait_context")
        self._add_import_code("pait.grpc.plugin.gateway", "BaseStaticGrpcGatewayRoute")
        self._add_import_code("pait.model.tag", "Tag")
        self._add_import_code("pait.model.response", "BaseResponseModel")
        self._add_import_code("pait.model.response", "JsonResponseModel")
        self._add_import_code("pydantic", "BaseModel")
        self._add_import_code("typing", "Any")
        self._add_import_code("typing", "Callable")
        self._add_import_code("typing", "List")
        self._add_import_code("typing", "Type")

        self._add_import_code(".", model_module_name)
        self._add_import_code(".", message_module_name)
        self._add_import_code(".", stub_module_name)

        ##########################################################
        # Extract information in preparation for code generation #
        ##########################################################
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
                # TODO A more elegant implementation of the google.protocol type
                if "Empty" in (input_type_name, output_type_name):
                    self._add_import_code("google.protobuf.empty_pb2", "Empty")
                grpc_method_url: str = f"/{self._fd.package}-{service.name}/{method.name}"
                if not service_model_list:
                    service_model_list.append(GrpcServiceOptionModel(url=grpc_method_url))
                for model_index, grpc_service_option_model in enumerate(service_model_list):
                    if not grpc_service_option_model.url:
                        grpc_service_option_model.url = grpc_method_url
                    request_message_model_name = f"{model_module_name}.{input_type_name}"
                    response_message_model_name = f"{model_module_name}.{output_type_name}"

                    ###################
                    # rebuild Message #
                    ###################
                    # Generating code directly would be very cumbersome, so here is a simplification
                    if (
                        grpc_service_option_model.request_message.exclude_column_name
                        or grpc_service_option_model.request_message.nested
                    ) and input_type_name != "Empty":
                        exclude_column_name_str = self._get_value_code(
                            grpc_service_option_model.request_message.exclude_column_name, sort=False
                        )
                        nested_str = self._get_value_code(grpc_service_option_model.request_message.nested, sort=False)

                        # self._add_import_code(f".{model_module_name}", input_type_name)
                        self._add_import_code("pait.grpc", "rebuild_message_type")
                        request_message_model_name = (
                            f"{input_type_name}{''.join([i.title() for i in func_name.split('_')])}"
                        )
                        self._add_import_code(
                            f".{model_module_name}", input_type_name, f" as {request_message_model_name}"
                        )
                        self._content_deque.append(
                            dedent(
                                f"""
                            {request_message_model_name} = rebuild_message_type(  # type: ignore[misc]
                                {request_message_model_name},
                                "{func_name}",
                                exclude_column_name={exclude_column_name_str},
                                nested={nested_str},
                            )
                            """
                            )
                        )
                    if (
                        grpc_service_option_model.response_message.exclude_column_name
                        or grpc_service_option_model.response_message.nested
                    ) and output_type_name != "Empty":
                        # self._add_import_code(f".{model_module_name}", output_type_name)
                        self._add_import_code("pait.grpc", "rebuild_message_type")
                        exclude_column_name_str = self._get_value_code(
                            grpc_service_option_model.response_message.exclude_column_name, sort=False
                        )
                        nested_str = self._get_value_code(grpc_service_option_model.response_message.nested, sort=False)
                        response_message_model_name = (
                            f"{output_type_name}{''.join([i.title() for i in func_name.split('_')])}"
                        )
                        self._add_import_code(
                            f".{model_module_name}", output_type_name, f" as {response_message_model_name}"
                        )
                        self._content_deque.append(
                            dedent(
                                f"""
                            {response_message_model_name} = rebuild_message_type(  # type: ignore[misc]
                                {response_message_model_name},
                                "{func_name}",
                                exclude_column_name={exclude_column_name_str},
                                nested={nested_str},
                            )
                            """
                            )
                        )
                    grpc_model_list.append(
                        GrpcModel(
                            index=model_index,
                            attr_prefix=self.attr_prefix,
                            filename=self._fd.name,
                            gateway_name=self.gateway_name,
                            method=method.name,
                            func_name=func_name,
                            input_type_name=input_type_name,
                            output_type_name=output_type_name,
                            request_message_model_name=request_message_model_name
                            if input_type_name not in ("Empty",)
                            else input_type_name,
                            response_message_model_name=response_message_model_name
                            if output_type_name not in ("Empty",)
                            else output_type_name,
                            request_message_name=f"{message_module_name}.{input_type_name}"
                            if input_type_name not in ("Empty",)
                            else input_type_name,
                            response_message_name=f"{message_module_name}.{output_type_name}"
                            if output_type_name not in ("Empty",)
                            else output_type_name,
                            stub_service_name=f"{service.name}_stub",
                            service_name=service.name,
                            model_module_name=model_module_name,
                            message_module_name=message_module_name,
                            stub_module_name=stub_module_name,
                            package=self._fd.package,
                            grpc_method_url=grpc_method_url,
                            grpc_service_option_model=grpc_service_option_model,
                            grpc_descriptor_method=method,
                            grpc_descriptor_service=service,
                            response_class_name=(
                                self._fd.package.title().replace("_", "") + output_type_name + "JsonResponseModel"
                            ),
                            gen_code=self,
                        )
                    )

        #######################################################################
        # Refine the information through the GRPC model and generate the code #
        #######################################################################
        route_code_str_list: List[str] = []
        response_code_str_list: List[str] = []

        simple_route_str_list: List[str] = []
        wrapper_route_str_list = []

        for grpc_model in grpc_model_list:
            # Specifies that the data is not parsed and skipped
            grpc_service_option_model = grpc_model.grpc_service_option_model
            if not grpc_service_option_model.enable:
                continue

            # Generate the data needed by `pait`
            self._add_import_code("pait.model.tag", "Tag")

            if grpc_model.index == 0:
                # The response model code only needs to be generated once
                template_dict: dict = asdict(grpc_model)
                response_code_str_list.append(self.get_response_code(grpc_model, template_dict) + "\n")

            base_func_name: str = grpc_model.func_name
            if grpc_model.index:
                base_func_name = base_func_name + "_" + str(grpc_model.index)
            pait_name: str = base_func_name + "_pait"
            wrapper_route_str_list.append(self.get_pait_code(tab_str, pait_name, grpc_model))
            for is_async in [True, False]:
                if grpc_model.index == 0:
                    # The routing function only needs to be generated once
                    template_dict = asdict(grpc_model)
                    template_dict["is_async"] = is_async
                    if is_async:
                        template_dict["func_name"] = "async_" + template_dict["func_name"]
                    route_code_str_list.append(self.get_route_code(grpc_model, template_dict) + "\n")
                func_name = grpc_model.func_name
                if is_async:
                    func_name = "async_" + func_name
                real_func_name: str = "pait_" + func_name
                if grpc_model.index:
                    real_func_name += "_" + str(grpc_model.index)
                wrapper_route_str_list.append(
                    f'{tab_str * 2}{real_func_name} = {pait_name}(feature_code="{grpc_model.index}")({func_name})'
                )

                if grpc_model.index:
                    wrapper_route_str_list.append(
                        f'{tab_str * 2}{real_func_name}.__name__ = "{real_func_name}"\n'
                        f"{tab_str * 2}{real_func_name}.__qualname__ = "
                        f'{real_func_name}.__qualname__.replace("{func_name}", "{real_func_name}")'
                    )
            simple_route_str_list.append(
                f"{tab_str * 3}SimpleRoute(\n"
                f'{tab_str * 4}url="{grpc_service_option_model.url}", \n'
                f'{tab_str * 4}methods=["{grpc_service_option_model.http_method}"], \n'
                f"{tab_str * 4}route=pait_async_{base_func_name}"
                f" if self.is_async else pait_{base_func_name}\n"
                f"{tab_str * 3})"
            )

        class_stub_str: str = ""
        stub_service_name_list: List[str] = []
        for service_name in set(service_name_list):
            stub_service_name: str = f"{service_name}_stub"
            stub_service_name_list.append(stub_service_name)
            class_stub_str += f"{tab_str * 1}{stub_service_name}: {stub_module_name}.{service_name}Stub\n"

        class_stub_str += (
            f"{tab_str * 1}stub_str_list: List[str] = {self._get_value_code(stub_service_name_list, sort=False)}\n"
        )
        class_str: str = (
            f"class {self.gateway_name}(BaseStaticGrpcGatewayRoute):\n"
            f"{class_stub_str}\n"
            f"{tab_str * 1}def gen_route(self) -> None:\n"
            f'{tab_str * 2}set_app_attribute(self.app, "{self.attr_prefix}_{self._fd.name}_gateway", self)\n'
            f"{tab_str * 2}# The response model generated based on Protocol is important and needs to be put first\n"
            f"{tab_str * 2}response_model_list: List[Type[BaseResponseModel]] = self._pait.response_model_list or []\n"
            f"{chr(10).join(wrapper_route_str_list) if wrapper_route_str_list else ''}\n"
            f"{tab_str * 2}self._add_multi_simple_route(\n"
            f"{tab_str * 3}self.app,\n"
            f"{(',' + chr(10)).join(simple_route_str_list) + ',' if simple_route_str_list else ''}\n"
            f"{tab_str * 3}prefix=self.prefix,\n"
            f"{tab_str * 3}title=self.title,\n"
            f"{tab_str * 3}** self.kwargs\n"
            f"{tab_str * 2})\n"
        )
        logger.debug(class_str)
        for response_code_str in response_code_str_list:
            self._content_deque.append(response_code_str)
        for route_code_str in route_code_str_list:
            self._content_deque.append(route_code_str)
        self._content_deque.append(class_str)
