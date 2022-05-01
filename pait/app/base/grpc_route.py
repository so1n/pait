import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from google.protobuf.json_format import MessageToDict  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel, Field

from pait.core import Pait
from pait.field import BaseField, Body, Depends
from pait.model.response import PaitJsonResponseModel
from pait.model.tag import Tag
from pait.util.grpc_inspect.message_to_pydantic import parse_msg_to_pydantic_model
from pait.util.grpc_inspect.stub import GrpcModel, ParseStub

grpc_tag: Tag = Tag("grpc", desc="grpc route")


class GrpcPaitModel(BaseModel):
    name: str = Field("")
    tag: List[Tuple[str, str]] = Field(default_factory=list)
    group: str = Field("")
    desc: str = Field("")
    summary: str = Field("")
    url: str = Field("")
    enable: bool = Field(True)


def get_pait_info_from_grpc_desc(grpc_model: GrpcModel) -> GrpcPaitModel:
    pait_dict: dict = {}
    for line in grpc_model.service_desc.split("\n") + grpc_model.desc.split("\n"):
        line = line.strip()
        if not line.startswith("pait: {"):
            continue
        line = line.replace("pait:", "")
        pait_dict.update(json.loads(line))
    return GrpcPaitModel(**pait_dict)


class GrpcRouter(object):
    pait: Pait
    make_response: Callable

    def __init__(
        self,
        stub: Any,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        pait: Optional[Pait] = None,
        make_response: Optional[Callable] = None,
        url_handler: Callable[[str], str] = lambda x: x.replace(".", "-"),
        request_param_field_dict: Optional[Dict[str, Union[Type[BaseField], Depends]]] = None,
    ):
        self.prefix: str = prefix
        self.title: str = title
        self.parser: ParseStub = ParseStub(stub)
        self.msg_to_dict: Callable = msg_to_dict

        self.url_handler: Callable[[str], str] = url_handler
        self._request_param_field_dict: Dict[str, Union[Type[BaseField], Depends]] = request_param_field_dict or {}
        self._pait: Pait = pait or self.pait
        self._make_response: Callable = make_response or self.make_response
        self._is_gen: bool = False
        self._tag_dict: Dict[str, Tag] = {}

    def _gen_route_func(self, method_name: str, grpc_model: GrpcModel) -> Tuple[Optional[Callable], GrpcPaitModel]:
        grpc_pait_model: GrpcPaitModel = get_pait_info_from_grpc_desc(grpc_model)
        if not grpc_pait_model.url:
            grpc_pait_model.url = method_name
        if grpc_pait_model.enable is False:
            return None, grpc_pait_model
        request_pydantic_model_class: Type[BaseModel] = parse_msg_to_pydantic_model(
            grpc_model.request, default_field=Body, request_param_field_dict=self._request_param_field_dict
        )

        tag_tuple: Tuple[Tag, ...] = (grpc_tag,)
        for tag, desc in grpc_pait_model.tag + [("grpc" + "-" + method_name.split("/")[1].split(".")[0], "")]:
            if tag in self._tag_dict:
                pait_tag: Tag = self._tag_dict[tag]
            else:
                pait_tag = Tag(tag, desc)
                self._tag_dict[tag] = pait_tag
            tag_tuple += (pait_tag,)

        if hasattr(grpc_model.func, "_loop"):

            async def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
                grpc_msg: Message = await grpc_model.func(
                    grpc_model.request(**request_pydantic_model.dict())  # type: ignore
                )
                return self.make_response(self.msg_to_dict(grpc_msg))

        else:

            def _route(request_pydantic_model: request_pydantic_model_class) -> Any:  # type: ignore
                grpc_msg: Message = grpc_model.func(grpc_model.request(**request_pydantic_model.dict()))  # type: ignore
                return self.make_response(self.msg_to_dict(grpc_msg))

        # change route func name and qualname
        _route.__name__ = method_name.replace(".", "_")
        _route.__qualname__ = _route.__qualname__.replace("._route", "." + _route.__name__)

        class CustomerJsonResponseModel(PaitJsonResponseModel):
            name: str = grpc_model.response.DESCRIPTOR.name
            response_data: Type[BaseModel] = parse_msg_to_pydantic_model(grpc_model.response)

        _route = self._pait(
            name=grpc_pait_model.name,
            group=grpc_pait_model.group or method_name.split("/")[1],
            tag=tag_tuple,
            desc=grpc_pait_model.desc,
            summary=grpc_pait_model.summary,
            response_model_list=[CustomerJsonResponseModel],
        )(_route)
        return _route, grpc_pait_model

    def _gen_route(self, app: Any) -> Any:  # type: ignore
        raise NotImplementedError()

    def gen_route(self, app: Any) -> Any:
        if self._is_gen:
            raise RuntimeError("Grpc route has been generated")
        self._gen_route(app)
        self._is_gen = True
