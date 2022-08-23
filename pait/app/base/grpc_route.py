import asyncio
from abc import ABCMeta
from sys import modules
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import grpc
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

from pait.core import Pait
from pait.field import BaseField, Body, Query
from pait.model.response import PaitBaseResponseModel, PaitJsonResponseModel
from pait.model.tag import Tag
from pait.util.grpc_inspect.stub import GrpcModel, ParseStub
from pait.util.grpc_inspect.types import Message, MessageToDict


def _gen_response_model_handle(grpc_model: GrpcModel) -> Type[PaitBaseResponseModel]:
    class CustomerJsonResponseModel(PaitJsonResponseModel):
        name: str = grpc_model.response.DESCRIPTOR.name
        description: str = grpc_model.response.__doc__ or ""

        # Rename it,
        # otherwise it will overwrite the existing scheme with the same name when generating OpenAPI documents.
        response_data: Type[BaseModel] = type(
            f"{grpc_model.method}RespModel", (msg_to_pydantic_model(grpc_model.response),), {}
        )

    return CustomerJsonResponseModel


class BaseGrpcGatewayRoute(object):
    pait: Pait
    make_response: Callable
    channel: Union[grpc.Channel, grpc.aio.Channel]

    _grpc_tag: Tag = Tag("grpc", desc="grpc route")

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
        gen_response_model_handle: Optional[Callable[[GrpcModel], Type[PaitBaseResponseModel]]] = None,
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
        :param gen_response_model_handle: Methods for generating Open API response objects
        """
        self.prefix: str = prefix
        self.title: str = title
        self._parse_msg_desc: Optional[str] = parse_msg_desc
        self.parse_stub_list: List[ParseStub] = [ParseStub(i) for i in stub_list]
        self.stub_list: Tuple[Any, ...] = stub_list
        self.msg_to_dict: Callable = msg_to_dict
        self.parse_dict: Optional[Callable] = parse_dict

        self.url_handler: Callable[[str], str] = url_handler
        self._gen_response_model_handle: Callable[[GrpcModel], Type[PaitBaseResponseModel]] = (
            gen_response_model_handle or _gen_response_model_handle
        )
        self._pait: Pait = pait or self.pait
        self._make_response: Callable = make_response or self.make_response
        self._is_gen: bool = False
        self._tag_dict: Dict[str, Tag] = {}
        self.method_func_dict: Dict[str, Callable] = {}

        self._add_route(app)

    def _gen_request_pydantic_class_from_message(self, message: Type[Message], http_method: str) -> Type[BaseModel]:
        """Generate the corresponding request body according to the grpc message(pydantic request)"""
        if http_method == "GET":
            default_field: Type[BaseField] = Query
        elif http_method == "POST":
            default_field = Body
        else:
            raise RuntimeError(f"{http_method} is not supported")
        return msg_to_pydantic_model(
            message,
            default_field=default_field,
            comment_prefix="pait",
            parse_msg_desc_method=getattr(message, "_message_module")
            if self._parse_msg_desc == "by_mypy"
            else self._parse_msg_desc,
        )

    def _gen_pait_from_grpc_model(self, grpc_model: GrpcModel) -> Pait:
        """Generate the corresponding pait instance according to the object of the grpc calling method"""
        tag_list: List[Tag] = [self._grpc_tag]
        for tag, desc in grpc_model.grpc_service_model.tag + [
            ("grpc" + "-" + grpc_model.method.split("/")[1].split(".")[0], "")
        ]:
            if tag in self._tag_dict:
                pait_tag: Tag = self._tag_dict[tag]
            else:
                pait_tag = Tag(tag, desc)
                self._tag_dict[tag] = pait_tag
            tag_list.append(pait_tag)

        response_model_list: List[Type[PaitBaseResponseModel]] = [self._gen_response_model_handle(grpc_model)]
        if self._pait._response_model_list:
            response_model_list.extend(self._pait._response_model_list)

        return self._pait.create_sub_pait(
            name=grpc_model.grpc_service_model.name,
            group=grpc_model.grpc_service_model.group or grpc_model.method.split("/")[1],
            append_tag=tuple(tag_list),
            desc=grpc_model.grpc_service_model.desc,
            summary=grpc_model.grpc_service_model.summary,
            response_model_list=response_model_list,
        )

    def get_grpc_func(self, method_name: str) -> Callable:
        """Get grpc invoke func"""
        func: Optional[Callable] = self.method_func_dict.get(method_name, None)
        if not func:
            raise RuntimeError(f"{method_name}'s func is not found, Please call init_channel to register the channel")
        return func

    def get_msg_from_dict(self, msg: Type[Message], request_dict: dict) -> Message:
        """Convert the Json data to the corresponding grpc Message object"""
        if self.parse_dict:
            request_msg: Message = self.parse_dict(request_dict, msg)
        else:
            request_msg = msg(**request_dict)  # type: ignore
        return request_msg

    def get_dict_from_msg(self, msg: Message) -> dict:
        """Convert the value of the Message object to Json data"""
        return self.msg_to_dict(msg)

    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        """Generate the routing function corresponding to grpc invoke fun"""
        raise NotImplementedError()

    def _gen_route_func(self, grpc_model: GrpcModel) -> Optional[Callable]:
        if grpc_model.grpc_service_model.enable is False:
            return None

        request_pydantic_model_class: Type[BaseModel] = self._gen_request_pydantic_class_from_message(
            grpc_model.request, grpc_model.grpc_service_model.http_method
        )
        pait: Pait = self._gen_pait_from_grpc_model(grpc_model)

        _route = self.gen_route(grpc_model, request_pydantic_model_class)
        # request_pydantic_model_class is not generated by this module,
        # so you need to inject request_pydantic_model_class into this module.
        modules[_route.__module__].__dict__["request_pydantic_model_class"] = request_pydantic_model_class
        # change route func name and qualname
        _route.__name__ = self.title + grpc_model.alias_method.replace(".", "_")
        _route.__qualname__ = _route.__qualname__.replace("._route", "." + _route.__name__)

        _route = pait(feature_code=grpc_model.method)(_route)
        return _route

    def _add_route(self, app: Any) -> Any:  # type: ignore
        """Add the generated routing function to the corresponding web framework instance"""
        raise NotImplementedError()

    def reinit_channel(
        self, channel: Union[grpc.Channel, grpc.aio.Channel]
    ) -> Union[grpc.Channel, grpc.aio.Channel, None]:
        """reload grpc channel"""
        old_channel: Union[grpc.Channel, grpc.aio.Channel, None] = getattr(self, "channel", None)
        self.init_channel(channel)
        return old_channel

    def _init_channel(self, channel: Union[grpc.Channel, grpc.aio.Channel]) -> None:
        """init grpc channel"""
        self.channel: Union[grpc.Channel, grpc.aio.Channel] = channel
        for stub_class in self.stub_list:
            stub = stub_class(channel)
            for func in stub.__dict__.values():
                method = func._method  # type: ignore
                if isinstance(method, bytes):
                    method = method.decode()
                self.method_func_dict[method] = func

    def init_channel(self, channel: Union[grpc.Channel, grpc.aio.Channel]) -> None:
        raise NotImplementedError()


class GrpcGatewayRoute(BaseGrpcGatewayRoute, metaclass=ABCMeta):
    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
            func: Callable = self.get_grpc_func(grpc_model.method)
            request_dict: dict = request_pydantic_model.dict()  # type: ignore
            request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
            grpc_msg: Message = func(request_msg)
            return self._make_response(self.get_dict_from_msg(grpc_msg))

        return _route

    def init_channel(self, channel: grpc.Channel) -> None:
        self._init_channel(channel)


class AsyncGrpcGatewayRoute(BaseGrpcGatewayRoute, metaclass=ABCMeta):
    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        async def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
            func: Callable = self.get_grpc_func(grpc_model.method)
            request_dict: dict = request_pydantic_model.dict()  # type: ignore
            request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if loop != func._loop:  # type: ignore
                raise RuntimeError(
                    "Loop is not same, "
                    "the grpc channel must be initialized after the event loop of the api server is initialized"
                )
            else:
                grpc_msg: Message = await func(request_msg)
            return self._make_response(self.get_dict_from_msg(grpc_msg))

        return _route

    def init_channel(self, channel: grpc.aio.Channel) -> None:
        self._init_channel(channel)
