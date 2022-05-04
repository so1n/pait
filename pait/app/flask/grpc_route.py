from typing import Any, Callable

from flask import Blueprint, Flask, Response, jsonify

from pait.app.base.grpc_route import GrpcRouter as BaseGrpcRouter
from pait.app.flask import pait


def make_response(_: Any, resp_dict: dict) -> Response:
    return jsonify(resp_dict)


class GrpcRoute(BaseGrpcRouter):
    pait = pait
    make_response: Callable = make_response

    def _gen_route(self, app: Flask) -> Any:
        blueprint: Blueprint = Blueprint(self.title + self._stub.__class__.__name__, __name__, url_prefix=self.prefix)
        for method_name, grpc_model in self.parser.method_dict.items():
            _route, grpc_pait_model = self._gen_route_func(method_name, grpc_model)
            if not _route:
                continue
            # grpc http method only POST
            blueprint.add_url_rule(self.url_handler(grpc_pait_model.url), view_func=_route, methods=["POST"])
        app.register_blueprint(blueprint)
