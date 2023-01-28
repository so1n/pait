from typing import Any, Callable, List, Type

from google.protobuf.json_format import MessageToDict  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from tornado.web import Application, RequestHandler
from typing_extensions import Self  # type: ignore

from pait.app.base.grpc_route import AsyncGrpcGatewayRoute as BaseGrpcRouter
from pait.app.base.grpc_route import GrpcModel
from pait.app.tornado import pait as tornado_pait
from pait.app.tornado._simple_route import SimpleRoute, add_multi_simple_route


def tornado_make_response(_: Any, resp_dict: dict) -> dict:
    return resp_dict


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = tornado_pait
    make_response = tornado_make_response
    request_handler: Type[RequestHandler] = RequestHandler

    def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:
        async def _route(
            request_pydantic_model: request_pydantic_model_class,  # type: ignore
        ) -> dict:
            func: Callable = self.get_grpc_func(grpc_model.method)
            request_dict: dict = request_pydantic_model.dict()  # type: ignore
            request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
            grpc_msg: Message = await func(request_msg)
            resp_dict: dict = self._make_response(self.get_dict_from_msg(grpc_msg))
            return resp_dict

        return _route

    def _add_route(self, app: Application) -> Any:
        for parse_stub in self.parse_stub_list:
            simple_route: List[SimpleRoute] = []
            for _, grpc_model_list in parse_stub.method_list_dict.items():
                for grpc_model in grpc_model_list:
                    _route = self._gen_route_func(grpc_model)
                    if not _route:
                        continue
                    simple_route.append(
                        SimpleRoute(
                            url=self.url_handler(grpc_model.grpc_service_model.url),
                            route=_route,
                            methods=[grpc_model.grpc_service_model.http_method],
                        )
                    )
            add_multi_simple_route(
                app,
                *simple_route,
                prefix=self.prefix,
                title=self.title + parse_stub.name,
                request_handler=self.request_handler,
            )

        # prefix: str = self.prefix
        # if prefix.endswith("/"):
        #     prefix = prefix[:-1]
        # route_list: List = []
        # for parse_stub in self.parse_stub_list:
        #     for _, grpc_model_list in parse_stub.method_list_dict.items():
        #         for grpc_model in grpc_model_list:
        #             _route = self._gen_route_func(grpc_model)
        #             if not _route:
        #                 continue

        #             route_class = type(
        #                 grpc_model.method.split(".")[-1],
        #                 (self.request_handler,),
        #                 {"__model__": f"{__name__}.{self.__class__.__name__}.gen_route_func.<locals>"},
        #             )
        #             setattr(route_class, grpc_model.grpc_service_model.http_method.lower(), _route)

        #             route_list.append(
        #                 (r"{}{}".format(prefix, self.url_handler(grpc_model.grpc_service_model.url)), route_class)
        #             )

        # app.wildcard_router.add_rules(route_list)
        # from tornado.web import AnyMatches, Rule, _ApplicationRouter

        # app.default_router = _ApplicationRouter(app, [Rule(AnyMatches(), app.wildcard_router)])
