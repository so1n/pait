from typing import Any, Callable

from sanic import Blueprint, HTTPResponse, Sanic, response

from pait.app.base.grpc_route import GrpcRouter as BaseGrpcRouter
from pait.app.sanic import pait


def make_response(_: Any, resp_dict: dict) -> HTTPResponse:
    return response.json(resp_dict)


class GrpcRoute(BaseGrpcRouter):
    pait = pait
    make_response: Callable = make_response

    def _gen_route(self, app: Sanic) -> Any:
        for parse_stub in self.parse_stub_list:
            blueprint: Blueprint = Blueprint(self.title + parse_stub.name, self.prefix)
            for method_name, grpc_model in parse_stub.method_dict.items():
                _route, grpc_pait_model = self._gen_route_func(method_name, grpc_model)
                if not _route:
                    continue

                if not hasattr(grpc_model.func, "_loop"):
                    raise TypeError(f"grpc_model.func:{grpc_model.func} must be async function")
                # grpc http method only POST
                blueprint.add_route(_route, self.url_handler(grpc_pait_model.url), methods=["POST"])
            app.blueprint(blueprint)
