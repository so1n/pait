from typing import Any, Callable

from flask import Blueprint, Flask, Response, jsonify

from pait.app.base.grpc_route import GrpcGatewayRoute as BaseGrpcRouter
from pait.app.flask import pait


def make_response(_: Any, resp_dict: dict) -> Response:
    return jsonify(resp_dict)


class GrpcGatewayRoute(BaseGrpcRouter):
    pait = pait
    make_response: Callable = make_response

    def _add_route(self, app: Flask) -> Any:
        for parse_stub in self.parse_stub_list:
            blueprint: Blueprint = Blueprint(self.title + parse_stub.name, __name__, url_prefix=self.prefix)
            for method_name, grpc_model in parse_stub.method_dict.items():
                _route, grpc_pait_model = self._gen_route_func(method_name, grpc_model)
                if not _route:
                    continue
                # grpc http method only POST
                blueprint.add_url_rule(self.url_handler(grpc_pait_model.url), view_func=_route, methods=["POST"])
            app.register_blueprint(blueprint)
