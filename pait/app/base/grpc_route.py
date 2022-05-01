from typing import Any, Callable, Dict, Optional, Type

from google.protobuf.json_format import MessageToDict  # type: ignore
from pydantic import BaseModel

from pait.core import Pait
from pait.field import BaseField, Body
from pait.model.response import PaitJsonResponseModel
from pait.model.tag import Tag
from pait.util.grpc_inspect.message_to_pydantic import parse_msg_to_pydantic_model
from pait.util.grpc_inspect.stub import GrpcModel, ParseStub

grpc_tag: Tag = Tag("grpc", desc="grpc route")


class GrpcRouter(object):
    pait: Pait

    def __init__(
        self,
        stub: Any,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        pait: Optional[Pait] = None,
        url_handler: Callable[[str], str] = lambda x: x.replace(".", "-"),
        request_param_field_dict: Optional[Dict[str, Type[BaseField]]] = None,
    ):
        self.prefix: str = prefix
        self.title: str = title
        self.parser: ParseStub = ParseStub(stub)
        self.msg_to_dict: Callable = msg_to_dict

        self.url_handler: Callable[[str], str] = url_handler
        self._request_param_field_dict: Dict[str, Type[BaseField]] = request_param_field_dict or {}
        self._pait: Pait = pait or self.pait
        self._is_gen: bool = False
        self._tag_dict: Dict[str, Tag] = {}

    def _gen_route_func(self, method_name: str, grpc_model: GrpcModel, resp_handle_func: Callable) -> Callable:
        request_pydantic_model_class: Type[BaseModel] = parse_msg_to_pydantic_model(
            grpc_model.request, default_field=Body, request_param_field_dict=self._request_param_field_dict
        )
        group: str = method_name.split("/")[1]
        tag: str = "grpc" + "-" + group.split(".")[0]
        if tag in self._tag_dict:
            pait_tag: Tag = self._tag_dict[tag]
        else:
            pait_tag = Tag(tag)
            self._tag_dict[tag] = pait_tag

        class CustomerJsonResponseModel(PaitJsonResponseModel):
            name: str = grpc_model.response.DESCRIPTOR.name
            response_data: Type[BaseModel] = parse_msg_to_pydantic_model(grpc_model.response)

        def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
            return resp_handle_func(
                self.msg_to_dict(grpc_model.func(grpc_model.request(**request_pydantic_model.dict())))  # type: ignore
            )

        _route.__name__ = method_name.replace(".", "_")
        _route.__qualname__ = _route.__qualname__.replace("._route", "." + _route.__name__)

        self._pait(
            group=group,
            tag=(
                pait_tag,
                grpc_tag,
            ),
            response_model_list=[CustomerJsonResponseModel],
        )(_route)
        return _route

    def _gen_route(self, app: Any) -> Any:  # type: ignore
        raise NotImplementedError()

    def gen_route(self, app: Any) -> Any:
        if self._is_gen:
            raise RuntimeError("Grpc route has been generated")
        self._gen_route(app)
        self._is_gen = True
