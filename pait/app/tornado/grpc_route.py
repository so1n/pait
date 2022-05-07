from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from google.protobuf.json_format import MessageToDict  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from tornado.web import Application, RequestHandler

from pait.app.base.grpc_route import GrpcGatewayRoute as BaseGrpcRouter
from pait.app.base.grpc_route import GrpcModel, GrpcPaitModel, get_pait_info_from_grpc_desc
from pait.app.tornado import pait as tornado_pait
from pait.core import Pait
from pait.field import BaseField, Depends
from pait.util.grpc_inspect.message_to_pydantic import GRPC_TIMESTAMP_HANDLER_TUPLE_T


def tornado_make_response(_: Any, resp_dict: dict) -> dict:
    return resp_dict


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = tornado_pait
    make_response = tornado_make_response

    def __init__(
        self,
        app: Any,
        *stub: Any,
        parse_msg_desc: Optional[str] = None,
        prefix: str = "",
        title: str = "",
        msg_to_dict: Callable = MessageToDict,
        parse_dict: Optional[Callable] = None,
        pait: Optional[Pait] = None,
        make_response: Optional[Callable] = None,
        url_handler: Callable[[str], str] = lambda x: x.replace(".", "-"),
        request_param_field_dict: Optional[Dict[str, Union[Type[BaseField], Depends]]] = None,
        grpc_timestamp_handler_tuple: Optional[GRPC_TIMESTAMP_HANDLER_TUPLE_T] = None,
        tornado_request_handler: Optional[Type[RequestHandler]] = None,
    ):
        self.tornado_request_handler: Type[RequestHandler] = tornado_request_handler or RequestHandler

        super().__init__(
            app,
            *stub,
            parse_msg_desc=parse_msg_desc,
            prefix=prefix,
            title=title,
            msg_to_dict=msg_to_dict,
            parse_dict=parse_dict,
            pait=pait,
            make_response=make_response,
            url_handler=url_handler,
            request_param_field_dict=request_param_field_dict,
            grpc_timestamp_handler_tuple=grpc_timestamp_handler_tuple,
        )

    def _gen_route_func(self, method_name: str, grpc_model: GrpcModel) -> Tuple[Optional[Callable], GrpcPaitModel]:
        grpc_pait_model: GrpcPaitModel = get_pait_info_from_grpc_desc(grpc_model)
        if grpc_pait_model.enable is False:
            return None, grpc_pait_model
        if not grpc_pait_model.url:
            grpc_pait_model.url = method_name

        request_pydantic_model_class: Type[BaseModel] = self._gen_request_pydantic_class_from_grpc_model(grpc_model)
        pait: Pait = self._gen_pait_from_grpc_method(method_name, grpc_model, grpc_pait_model)

        if not hasattr(grpc_model.func, "_loop"):
            raise TypeError(f"grpc_model.func:{grpc_model.func} must be async function")
        grpc_route: "GrpcGatewayRoute" = self

        async def _route(  # type: ignore
            self,  # type: ignore
            request_pydantic_model: request_pydantic_model_class,  # type: ignore
        ) -> None:
            request_dict: dict = request_pydantic_model.dict()  # type: ignore
            if grpc_route.parse_dict:
                request_msg: Message = grpc_route.parse_dict(request_dict, grpc_model.request())
            else:
                request_msg = grpc_model.request(**request_dict)  # type: ignore

            grpc_msg: Message = await grpc_model.func(request_msg)
            resp_dict: dict = grpc_route._make_response(grpc_route.msg_to_dict(grpc_msg))  # type: ignore
            self.write(resp_dict)

        # change route func name and qualname
        _route.__name__ = method_name.replace(".", "_")
        _route.__qualname__ = _route.__qualname__.replace("._route", "." + _route.__name__)

        route_class = type(
            grpc_model.method.split(".")[-1],
            (self.tornado_request_handler,),
            {"__model__": f"{__name__}.{self.__class__.__name__}.gen_route_func.<locals>"},
        )
        setattr(route_class, "post", pait(feature_code=grpc_model.method)(_route))

        return route_class, grpc_pait_model

    def _gen_route(self, app: Application) -> Any:
        prefix: str = self.prefix
        if prefix.endswith("/"):
            prefix = prefix[:-1]
        route_list: List = []
        for parse_stub in self.parse_stub_list:
            for method_name, grpc_model in parse_stub.method_dict.items():
                _route, grpc_pait_model = self._gen_route_func(method_name, grpc_model)
                if not _route:
                    continue

                if not hasattr(grpc_model.func, "_loop"):
                    raise TypeError(f"grpc_model.func:{grpc_model.func} must be async function")

                # grpc http method only POST
                route_list.append((r"{}{}".format(prefix, self.url_handler(grpc_pait_model.url)), _route))

        app.wildcard_router.add_rules(route_list)
        from tornado.web import AnyMatches, Rule, _ApplicationRouter

        app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])
