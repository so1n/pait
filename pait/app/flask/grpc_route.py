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
            for _, grpc_model_list in parse_stub.method_list_dict.items():
                for grpc_model in grpc_model_list:
                    _route = self._gen_route_func(grpc_model)
                    if not _route:
                        continue
                    blueprint.add_url_rule(
                        self.url_handler(grpc_model.grpc_service_model.url),
                        view_func=_route,
                        methods=[grpc_model.grpc_service_model.http_method],
                    )
            app.register_blueprint(blueprint)
