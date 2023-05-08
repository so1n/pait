from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

import grpc
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from pait.app.any.util import import_func_from_app
from pait.core import Pait
from pait.grpc.util import rebuild_dict
from pait.model import Tag

MessageT = TypeVar("MessageT", bound=Message)

__all__ = ["BaseGrpcGatewayRoute"]


class BaseGrpcGatewayRoute(object):
    pait: Pait
    _make_response: staticmethod = staticmethod(lambda x: x)
    add_multi_simple_route: staticmethod
    channel: Union[grpc.Channel, grpc.aio.Channel]

    _grpc_tag: Tag = Tag("grpc", desc="grpc route")

    def __init__(
        self,
        app: Any,
        parse_msg_desc: Optional[str] = None,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        parse_dict: Optional[Callable] = None,
        pait: Optional[Pait] = None,
        make_response: Optional[Callable] = None,
        add_multi_simple_route: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """
        :param app: Instance object of the web framework
        :param parse_msg_desc: The way to parse protobuf message, see the specific usage method：
            https://github.com/so1n/protobuf_to_pydantic#22parameter-verification
        :param prefix: url prefix
        :param title: Title of gRPC Gateway, if there are multiple gRPC Gateways in the same Stub,
            you need to ensure that the title of each gRPC Gateway is different
        :param msg_to_dict: protobuf.json_format.msg_to_dict func
        :param parse_dict: protobuf.json_format.parse_dict func
        :param pait: instance of pait
        :param make_response: The method of converting Message to Response object
        :param add_multi_simple_route: A function that registers multiple routes with the app
        :param kwargs: Extended parameters supported by the `add multi simple route` function of different frameworks
        """
        self.app: Any = app
        self.prefix: str = prefix
        self.title: str = title
        self._parse_msg_desc: Optional[str] = parse_msg_desc
        self.msg_to_dict: Callable = msg_to_dict
        self.parse_dict: Optional[Callable] = parse_dict
        # If empty, try to get an available Pait
        self._pait: Pait = pait or getattr(self, "pait", None) or import_func_from_app("pait", app=app)  # type: ignore
        self._add_multi_simple_route = (
            add_multi_simple_route
            or getattr(self, "add_multi_simple_route", None)
            or import_func_from_app("add_multi_simple_route", app=app)
        )  # type: ignore
        self.make_response: Callable = make_response or self._make_response
        self._tag_dict: Dict[str, Tag] = {}

    def get_msg_from_dict(self, msg: Type[MessageT], request_dict: dict) -> MessageT:
        """Convert the Json data to the corresponding grpc Message object"""
        if self.parse_dict:
            request_msg: MessageT = self.parse_dict(request_dict, msg())
        else:
            request_msg = msg(**request_dict)  # type: ignore
        return request_msg

    def msg_from_dict_handle(self, msg: Type[MessageT], request_dict: dict, nested: Optional[list] = None) -> MessageT:
        if nested:
            for column in nested:
                request_dict = {column: request_dict}
        return self.get_msg_from_dict(msg, request_dict)

    def msg_to_dict_handle(
        self, message: Message, exclude_column_name: Optional[list] = None, nested: Optional[list] = None
    ) -> dict:
        message_dict = self.msg_to_dict(message)
        if exclude_column_name or nested:
            message_dict = rebuild_dict(
                message_dict,
                exclude_column_name=exclude_column_name,
                nested=nested,
            )
        return self.make_response(message_dict)

    def reinit_channel(
        self, channel: Union[grpc.Channel, grpc.aio.Channel], auto_close: bool = False
    ) -> Union[grpc.Channel, grpc.aio.Channel, None]:
        """reload grpc channel"""
        old_channel: Union[grpc.Channel, grpc.aio.Channel, None] = getattr(self, "channel", None)
        self.channel = channel
        # If it is grpc.aio.Channel, it will return the corresponding grpc.Channel first,
        # and then close it asynchronously
        if old_channel and auto_close:
            old_channel.close()
        return old_channel

    def init_channel(self, channel: Union[grpc.Channel, grpc.aio.Channel]) -> None:
        self.reinit_channel(channel, auto_close=True)
