from __future__ import annotations

import hashlib

from flask import Flask, Response, make_response
from flask.views import MethodView
from pydantic import BaseModel, ValidationError
from redis import Redis  # type: ignore

from example.common import tag
from example.common.request_model import SexEnum, UserOtherModel
from example.common.response_model import (
    FailRespModel,
    LoginRespModel,
    SimpleRespModel,
    SuccessRespModel,
    UserSuccessRespModel,
    link_login_token_model,
)
from example.common.utils import NotTipParamHandler
from example.flask_example.depend_route import (
    depend_contextmanager_route,
    depend_route,
    pre_depend_contextmanager_route,
)
from example.flask_example.field_route import (
    field_default_factory_route,
    pait_base_field_route,
    pait_model_route,
    post_route,
    same_alias_route,
)
from example.flask_example.grpc_route import add_grpc_gateway_route
from example.flask_example.plugin_route import (
    auto_complete_json_route,
    cache_response,
    cache_response1,
    check_json_plugin_route,
    check_json_plugin_route1,
    check_param_route,
    mock_route,
)
from example.flask_example.response_route import (
    check_response_route,
    file_response_route,
    html_response_route,
    text_response_route,
)
from example.flask_example.security_route import api_key_route
from example.flask_example.utils import api_exception, global_pait
from pait.app.flask import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.flask.plugin.cache_resonse import CacheResponsePlugin
from pait.exceptions import PaitBaseException
from pait.extra.config import MatchRule, apply_block_http_method_set, apply_extra_openapi_model
from pait.field import Header, Json, Query
from pait.g import config
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar

user_pait: Pait = global_pait.create_sub_pait(group="user")
link_pait: Pait = global_pait.create_sub_pait(
    group="links",
    status=PaitStatus.release,
    tag=(tag.links_tag,),
)
other_pait: Pait = pait.create_sub_pait(author=("so1n",), status=PaitStatus.test, group="other")


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> dict:
    """Prompted error from pait when test does not find value"""
    return {"code": 0, "msg": "", "data": {"content_type": content__type}}


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    param_handler_plugin=NotTipParamHandler,
)
def raise_not_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> dict:
    """Prompted error from pait when test does not find value"""
    return {"code": 0, "msg": "", "data": {"content_type": content__type}}


class CbvRoute(MethodView):
    content_type: str = Header.i(alias="Content-Type")

    @user_pait(
        status=PaitStatus.release,
        tag=(tag.cbv_tag,),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Query.i(description="sex"),
        model: UserOtherModel = Query.i(raw_return=True),
    ) -> dict:
        """Text cbv route get"""
        return {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "sex": sex.value,
                "age": model.age,
                "content_type": self.content_type,
            },
        }

    @user_pait(
        desc="test cbv post method",
        tag=(tag.cbv_tag,),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    def post(
        self,
        uid: int = Json.i(description="user id", gt=10, lt=1000),
        user_name: str = Json.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Json.i(description="sex"),
        model: UserOtherModel = Json.i(raw_return=True),
    ) -> dict:
        """Text cbv route post"""
        return {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "sex": sex.value,
                "age": model.age,
                "content_type": self.content_type,
            },
        }


class NotPaitCbvRoute(MethodView):
    user_name: str = Query.i()

    def get(self) -> Response:
        return make_response(self.user_name, 200)

    def post(self) -> Response:
        return make_response(self.user_name, 200)


@link_pait(response_model_list=[LoginRespModel])
def login_route(uid: str = Json.i(description="user id"), password: str = Json.i(description="password")) -> dict:
    # only use test
    return {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}


@link_pait(response_model_list=[SuccessRespModel])
def get_user_route(
    token: str = Header.i("", description="token", links=link_login_token_model, example=TemplateVar("token"))
) -> dict:
    if token:
        return {"code": 0, "msg": ""}
    else:
        return {"code": 1, "msg": ""}


def not_pait_route(
    user_name: str = Query.i(),
) -> Response:
    return make_response(user_name, 200)


def add_api_doc_route(app: Flask) -> None:
    """Split out to improve the speed of test cases"""
    add_doc_route(app, pin_code="6666", prefix="/", title="Pait Api Doc(private)")
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc", app=app)


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
    app.add_url_rule("/api/login", view_func=login_route, methods=["POST"])
    app.add_url_rule("/api/user", view_func=get_user_route, methods=["GET"])
    app.add_url_rule("/api/raise-tip", view_func=raise_tip_route, methods=["POST"])
    app.add_url_rule("/api/raise-not-tip", view_func=raise_not_tip_route, methods=["POST"])
    app.add_url_rule("/api/not-pait", view_func=not_pait_route, methods=["GET"])
    app.add_url_rule("/api/not-pait-cbv", view_func=NotPaitCbvRoute.as_view("NotPaitRoute"))
    app.add_url_rule("/api/cbv", view_func=CbvRoute.as_view("test_cbv"))

    app.add_url_rule("/api/field/post", view_func=post_route, methods=["POST"])
    app.add_url_rule("/api/field/pait-base-field/<age>", view_func=pait_base_field_route, methods=["POST"])
    app.add_url_rule("/api/field/field-default-factory", view_func=field_default_factory_route, methods=["POST"])
    app.add_url_rule("/api/field/same-alias", view_func=same_alias_route, methods=["GET"])
    app.add_url_rule("/api/field/pait-model", view_func=pait_model_route, methods=["POST"])

    app.add_url_rule("/api/resp/text-resp", view_func=text_response_route, methods=["GET"])
    app.add_url_rule("/api/resp/html-resp", view_func=html_response_route, methods=["GET"])
    app.add_url_rule("/api/resp/file-resp", view_func=file_response_route, methods=["GET"])
    app.add_url_rule("/api/resp/check-resp", view_func=check_response_route, methods=["GET"])

    app.add_url_rule("/api/plugin/mock/<age>", view_func=mock_route, methods=["GET"])
    app.add_url_rule("/api/plugin/check-json-plugin", view_func=check_json_plugin_route, methods=["GET"])
    app.add_url_rule("/api/plugin/cache-response", view_func=cache_response, methods=["GET"])
    app.add_url_rule("/api/plugin/cache-response-1", view_func=cache_response1, methods=["GET"])
    app.add_url_rule("/api/plugin/check-json-plugin-1", view_func=check_json_plugin_route1, methods=["GET"])
    app.add_url_rule("/api/plugin/auto-complete-json-plugin", view_func=auto_complete_json_route, methods=["GET"])
    app.add_url_rule("/api/plugin/check-param", view_func=check_param_route, methods=["GET"])

    app.add_url_rule("/api/depend/depend", view_func=depend_route, methods=["POST"])
    app.add_url_rule("/api/depend/depend-contextmanager", view_func=depend_contextmanager_route, methods=["GET"])
    app.add_url_rule(
        "/api/depend/pre-depend-contextmanager", view_func=pre_depend_contextmanager_route, methods=["GET"]
    )

    app.add_url_rule("/api/security/api-key", view_func=api_key_route, methods=["GET"])

    app.errorhandler(PaitBaseException)(api_exception)
    app.errorhandler(ValidationError)(api_exception)
    app.errorhandler(RuntimeError)(api_exception)
    # support not user @pait route
    load_app(app, auto_load_route=True)
    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.DEBUG
    )

    class ExtraModel(BaseModel):
        extra_a: str = Query.i(default="", description="Fields used to demonstrate the expansion module")
        extra_b: int = Query.i(default=0, description="Fields used to demonstrate the expansion module")

    config.init_config(
        apply_func_list=[
            apply_block_http_method_set({"HEAD", "OPTIONS"}),
            apply_extra_openapi_model(ExtraModel, match_rule=MatchRule(key="!tag", target="grpc")),
        ]
    )
    flask_app: Flask = create_app()
    add_grpc_gateway_route(flask_app)
    add_api_doc_route(flask_app)
    flask_app.run(port=8000, debug=True)