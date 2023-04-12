import asyncio
from abc import ABCMeta
from sys import modules
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import grpc
from google.protobuf.empty_pb2 import Empty  # type: ignore
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

from pait.app.base.simple_route import SimpleRoute
from pait.core import Pait
from pait.field import BaseField, Body, Query
from pait.grpc.base_gateway import BaseGrpcGatewayRoute
from pait.grpc.desc_template import DescTemplate
from pait.grpc.inspect import GrpcModel, Message, MessageToDict, ParseStub
from pait.grpc.util import rebuild_message_type
from pait.model import BaseResponseModel, JsonResponseModel, Tag

__all__ = ["DynamicGrpcGatewayRoute", "AsyncGrpcGatewayRoute", "GrpcGatewayRoute"]


def _gen_response_model_handle(grpc_model: GrpcModel) -> Type[BaseResponseModel]:
    if grpc_model.response is Empty:
        response_model: Any = dict
    elif grpc_model.grpc_service_option_model.response_message:
        response_model = rebuild_message_type(
            msg_to_pydantic_model(grpc_model.response),
            grpc_model.invoke_name,
            exclude_column_name=grpc_model.grpc_service_option_model.response_message.exclude_column_name,
            nested=grpc_model.grpc_service_option_model.response_message.nested,
        )
    else:
        response_model = msg_to_pydantic_model(grpc_model.response)

    class CustomerJsonResponseModel(JsonResponseModel):
        name: str = grpc_model.response.DESCRIPTOR.name
        description: str = grpc_model.response.__doc__ or ""

        # Rename it,
        # otherwise it will overwrite the existing scheme with the same name when generating OpenAPI documents.
        response_data: Type[BaseModel] = type(f"{grpc_model.grpc_method_url}RespModel", (response_model,), {})

    return CustomerJsonResponseModel


class DynamicGrpcGatewayRoute(BaseGrpcGatewayRoute):
    def __init__(
        self,
        app: Any,
        *stub_list: Any,
        parse_msg_desc: Optional[str] = None,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        parse_dict: Optional[Callable] = None,
        pait: Optional[Pait] = None,
        make_response: Optional[Callable] = None,
        url_handler: Callable[[str], str] = lambda x: x.replace(".", "-"),
        desc_template: Type[DescTemplate] = DescTemplate,
        gen_response_model_handle: Optional[Callable[[GrpcModel], Type[BaseResponseModel]]] = None,
        **kwargs: Any,
    ):
        """
        :param app: Instance object of the web framework
        :param stub_list: gRPC Stub List
        :param parse_msg_desc: The way to parse protobuf message, see the specific usage method：
            https://github.com/so1n/protobuf_to_pydantic#22parameter-verification
        :param prefix: url prefix
        :param title: Title of gRPC Gateway, if there are multiple gRPC Gateways in the same Stub,
            you need to ensure that the title of each gRPC Gateway is different
        :param msg_to_dict: protobuf.json_format.msg_to_dict func
        :param parse_dict: protobuf.json_format.parse_dict func
        :param pait: instance of pait
        :param make_response: The method of converting Message to Response object
        :param url_handler: url processing function, the default symbol: `.` is converted to `-`
        :param desc_template:
            DescTemplate object, which can extend and modify template adaptation rules through inheritance
        :param gen_response_model_handle: Methods for generating OpenAPI response objects
        :param kwargs: Extended parameters supported by the `add multi simple route` function of different frameworks
        """
        super().__init__(
            app=app,
            parse_msg_desc=parse_msg_desc,
            prefix=prefix,
            title=title,
            msg_to_dict=msg_to_dict,
            parse_dict=parse_dict,
            pait=pait,
            make_response=make_response,
            gen_response_model_handle=gen_response_model_handle,
            **kwargs,
        )
        self._gen_response_model_handle: Callable[[GrpcModel], Type[BaseResponseModel]] = (
            gen_response_model_handle or _gen_response_model_handle
        )
        self.desc_template: Type[DescTemplate] = desc_template
        self.stub_list: Tuple[Any, ...] = stub_list
        self.url_handler: Callable[[str], str] = url_handler
        self.grpc_method_url_func_dict: Dict[str, Callable] = {}
        self._add_route(app, **kwargs)

    def _gen_request_pydantic_class(self, grpc_model: GrpcModel) -> Type:
        """
        Generate a pydantic class that automatically generates the corresponding request according to the Protocol
         Message (Field is pait.field)
        """
        http_method: str = grpc_model.grpc_service_option_model.http_method
        if http_method == "GET":
            default_field: Type[BaseField] = Query
        elif http_method == "POST":
            default_field = Body
        else:
            raise RuntimeError(f"{http_method} is not supported")
        request_model: Type[BaseModel] = msg_to_pydantic_model(
            grpc_model.request,
            default_field=default_field,
            comment_prefix="pait",
            desc_template=self.desc_template,
            parse_msg_desc_method=getattr(grpc_model.request, "_message_module")
            if self._parse_msg_desc == "by_mypy"
            else self._parse_msg_desc,
        )
        if grpc_model.grpc_service_option_model.request_message:
            return rebuild_message_type(
                request_model,
                grpc_model.invoke_name,
                exclude_column_name=grpc_model.grpc_service_option_model.request_message.exclude_column_name,
                nested=grpc_model.grpc_service_option_model.request_message.nested,
            )
        else:
            return request_model

    def _gen_pait_from_grpc_model(self, grpc_model: GrpcModel) -> Pait:
        """Generate the corresponding pait instance according to the object of the grpc calling method"""
        tag_list: List[Tag] = [self._grpc_tag]
        for tag, desc in grpc_model.grpc_service_option_model.tag + [
            ("grpc" + "-" + self.url_handler(grpc_model.grpc_method_url.split("/")[1]), "")
        ]:
            if tag in self._tag_dict:
                pait_tag: Tag = self._tag_dict[tag]
            else:
                pait_tag = Tag(tag, desc)
                self._tag_dict[tag] = pait_tag
            tag_list.append(pait_tag)

        # The response model generated based on Protocol is important and needs to be put first
        response_model_list: List[Type[BaseResponseModel]] = [self._gen_response_model_handle(grpc_model)]
        if self._pait.response_model_list:
            response_model_list.extend(self._pait.response_model_list)

        return self._pait.create_sub_pait(
            name=grpc_model.grpc_service_option_model.name,
            group=grpc_model.grpc_service_option_model.group or grpc_model.grpc_method_url.split("/")[1],
            append_tag=tuple(tag_list),
            desc=grpc_model.grpc_service_option_model.desc,
            summary=grpc_model.grpc_service_option_model.summary,
            response_model_list=response_model_list,
        )

    def get_grpc_func(self, grpc_model: GrpcModel) -> Callable:
        """Get grpc invoke func"""
        func: Optional[Callable] = self.grpc_method_url_func_dict.get(grpc_model.grpc_method_url, None)
        if not func:
            raise RuntimeError(
                f"{grpc_model.grpc_method_url}'s func is not found, Please call init_channel to register the channel"
            )
        return func

    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type) -> Callable:
        """Generate the routing function corresponding to grpc invoke fun"""
        raise NotImplementedError()

    def _gen_route_func(self, grpc_model: GrpcModel) -> Optional[Callable]:
        if grpc_model.grpc_service_option_model.enable is False:
            return None

        request_pydantic_model_class: Type = self._gen_request_pydantic_class(grpc_model)
        pait: Pait = self._gen_pait_from_grpc_model(grpc_model)
        _route = self.gen_route(grpc_model, request_pydantic_model_class)

        # change route func name and qualname
        _route.__name__ = self.title + grpc_model.alias_grpc_method_url.replace(".", "_")
        _route.__qualname__ = _route.__qualname__.replace("._route", "." + _route.__name__)

        # Since the route is generated dynamically, pait will not be able to resolve the type of
        # 'request_pydantic_model_class', so it needs to inject 'request_pydantic_model_class' into the module
        # where the route is generated
        modules[_route.__module__].__dict__["request_pydantic_model_class"] = request_pydantic_model_class
        _route = pait(feature_code=grpc_model.grpc_method_url)(_route)
        return _route

    def _add_route(self, app: Any, **kwargs: Any) -> Any:  # type: ignore
        """Add the generated routing function to the corresponding web framework instance"""
        for stub_class in self.stub_list:
            parse_stub: ParseStub = ParseStub(stub_class)
            simple_route_list: List[SimpleRoute] = []
            for _, grpc_model_list in parse_stub.method_list_dict.items():
                for grpc_model in grpc_model_list:
                    _route = self._gen_route_func(grpc_model)
                    if not _route:
                        continue
                    simple_route_list.append(
                        SimpleRoute(
                            url=self.url_handler(grpc_model.grpc_service_option_model.url),
                            route=_route,
                            methods=[grpc_model.grpc_service_option_model.http_method],
                        )
                    )
            self._add_multi_simple_route(
                app, *simple_route_list, prefix=self.prefix, title=self.title + parse_stub.name, **kwargs
            )

    def reinit_channel(
        self, channel: Union[grpc.Channel, grpc.aio.Channel], auto_close: bool = False
    ) -> Union[grpc.Channel, grpc.aio.Channel, None]:
        for stub_class in self.stub_list:
            stub = stub_class(channel)
            for func in stub.__dict__.values():
                grpc_method_url = func._method  # type: ignore
                if isinstance(grpc_method_url, bytes):
                    grpc_method_url = grpc_method_url.decode()
                self.grpc_method_url_func_dict[grpc_method_url] = func
        return super().reinit_channel(channel, auto_close)


class GrpcGatewayRoute(DynamicGrpcGatewayRoute, metaclass=ABCMeta):
    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
            func: Callable = self.get_grpc_func(grpc_model)
            request_msg: Message = self.msg_from_dict_handle(
                grpc_model.request,
                request_pydantic_model.dict(),  # type: ignore
                grpc_model.grpc_service_option_model.request_message.nested,
            )

            grpc_msg: Message = func(request_msg)
            return self.msg_to_dict_handle(
                grpc_msg,
                grpc_model.grpc_service_option_model.response_message.exclude_column_name,
                grpc_model.grpc_service_option_model.response_message.nested,
            )

        return _route

    def reinit_channel(self, channel: grpc.Channel, auto_close: bool = False) -> Union[grpc.Channel, None]:
        return super().reinit_channel(channel, auto_close)


class AsyncGrpcGatewayRoute(DynamicGrpcGatewayRoute, metaclass=ABCMeta):
    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        async def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
            func: Callable = self.get_grpc_func(grpc_model)
            request_msg: Message = self.msg_from_dict_handle(
                grpc_model.request,
                request_pydantic_model.dict(),  # type: ignore
                grpc_model.grpc_service_option_model.request_message.nested,
            )
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if loop != func._loop:  # type: ignore
                raise RuntimeError(
                    "Loop is not same, "
                    "the grpc channel must be initialized after the event loop of the api server is initialized"
                )
            else:
                grpc_msg: Message = await func(request_msg)
            return self.msg_to_dict_handle(
                grpc_msg,
                grpc_model.grpc_service_option_model.response_message.exclude_column_name,
                grpc_model.grpc_service_option_model.response_message.nested,
            )

        return _route

    def init_channel(self, channel: grpc.aio.Channel) -> None:
        super().init_channel(channel)

    def reinit_channel(self, channel: grpc.aio.Channel, auto_close: bool = False) -> Union[grpc.aio.Channel, None]:
        return super().reinit_channel(channel, auto_close)
