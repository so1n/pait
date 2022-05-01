from typing import Any, Callable

from flask import Blueprint, Flask, Response, jsonify

from pait.app.base.grpc_route import GrpcRouter as BaseGrpcRouter
from pait.app.flask import pait


def make_response(resp_dict: dict) -> Response:
    return jsonify(resp_dict)


class GrpcRoute(BaseGrpcRouter):
    pait = pait

    def _gen_route(self, app: Flask) -> Any:
        blueprint: Blueprint = Blueprint(self.title, __name__, url_prefix=self.prefix)
        for method_name, grpc_model in self.parser.method_dict.items():
            _route: Callable = self._gen_route_func(method_name, grpc_model, make_response)
            blueprint.add_url_rule(self.url_handler(method_name), view_func=_route, methods=["POST"])
        app.register_blueprint(blueprint)
