from typing import Any, Callable, List

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from pait.app.base.grpc_route import AsyncGrpcGatewayRoute as BaseGrpcRouter
from pait.app.starlette import pait


def make_response(_: Any, resp_dict: dict) -> Response:
    return JSONResponse(resp_dict)


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = pait
    make_response: Callable = make_response

    def _add_route(self, app: Starlette) -> Any:
        route_list: List[Route] = []
        for parse_stub in self.parse_stub_list:
            for _, grpc_model_list in parse_stub.method_list_dict.items():
                for grpc_model in grpc_model_list:
                    _route = self._gen_route_func(grpc_model)
                    if not _route:
                        continue

                    route_list.append(
                        Route(
                            self.url_handler(grpc_model.grpc_service_model.url),
                            _route,
                            methods=[grpc_model.grpc_service_model.http_method],
                        )
                    )
        app.routes.append(Mount(self.prefix, name=self.title, routes=route_list))
