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
            for method_name, grpc_model in parse_stub.method_dict.items():
                _route, grpc_pait_model = self._gen_route_func(method_name, grpc_model)
                if not _route:
                    continue

                # grpc http method only POST
                route_list.append(Route(self.url_handler(grpc_pait_model.url), _route, methods=["POST"]))
        app.routes.append(Mount(self.prefix, name=self.title, routes=route_list))
