from typing import Any, Callable, List, Optional, Type, Union

import grpc
from any_api.openapi import BaseResponseModel
from google.protobuf.json_format import MessageToDict

from pait.app import add_multi_simple_route as _add_multi_simple_route
from pait.core import Pait
from pait.grpc import BaseGrpcGatewayRoute, GrpcModel
from pait.util import get_real_annotation


class BaseStaticGrpcGatewayRoute(BaseGrpcGatewayRoute):
    add_multi_simple_route: staticmethod = staticmethod(_add_multi_simple_route)
    stub_str_list: List[str]

    def __init__(
        self,
        app: Any,
        is_async: bool,
        channel: Union[grpc.Channel, grpc.aio.Channel, None] = None,
        parse_msg_desc: Optional[str] = None,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        parse_dict: Optional[Callable] = None,
        pait: Optional[Pait] = None,
        make_response: Optional[Callable] = None,
        add_multi_simple_route: Optional[Callable] = None,
        gen_response_model_handle: Optional[Callable[[GrpcModel], Type[BaseResponseModel]]] = None,
        **kwargs: Any,
    ):
        """
        :param app: Instance object of the web framework
        :param channel: grpc Channel
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
        :param gen_response_model_handle: Methods for generating OpenAPI response objects
        :param kwargs: Extended parameters supported by the `add multi simple route` function of different frameworks
        """
        super().__init__(
            app,
            parse_msg_desc=parse_msg_desc,
            prefix=prefix,
            title=title,
            msg_to_dict=msg_to_dict,
            parse_dict=parse_dict,
            pait=pait,
            make_response=make_response,
            gen_response_model_handle=gen_response_model_handle,
            add_multi_simple_route=add_multi_simple_route,
            kwargs=kwargs,
        )
        self.is_async: bool = is_async
        self.kwargs: Any = kwargs
        if channel:
            self.reinit_channel(channel)
        self.gen_route()

    def gen_route(self) -> None:
        raise NotImplementedError

    def reinit_channel(
        self, channel: Union[grpc.Channel, grpc.aio.Channel], auto_close: bool = False
    ) -> Union[grpc.Channel, grpc.aio.Channel, None]:
        for stub_str in self.stub_str_list:
            setattr(self, stub_str, get_real_annotation(self.__annotations__[stub_str], self)(channel))
        return super().reinit_channel(channel, auto_close)
