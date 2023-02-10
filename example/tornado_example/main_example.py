from __future__ import annotations

import hashlib

import aiofiles  # type: ignore
from redis.asyncio import Redis  # type: ignore
from tornado.ioloop import IOLoop
from tornado.web import Application

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
from example.common.utils import NotTipAsyncParamHandler
from example.tornado_example.depend_route import (
    DependAsyncContextmanagerHanler,
    DependContextmanagerHanler,
    DependHandler,
    PreDependAsyncContextmanagerHanler,
    PreDependContextmanagerHanler,
)
from example.tornado_example.field_route import (
    FieldDefaultFactoryHandler,
    PaitBaseFieldHandler,
    PaitModelHanler,
    PostHandler,
    SameAliasHandler,
)
from example.tornado_example.grpc_route import add_grpc_gateway_route
from example.tornado_example.plugin_route import (
    AutoCompleteJsonHandler,
    CacheResponse1Handler,
    CacheResponseHandler,
    CheckJsonPlugin1Handler,
    CheckJsonPluginHandler,
    MockHandler,
    ParamAtMostOneOfByExtraParamHandler,
    ParamAtMostOneOfHandler,
    ParamRequiredByExtraParamHandler,
    ParamRequiredHandler,
)
from example.tornado_example.response_route import (
    CheckRespHandler,
    FileResponseHanler,
    HtmlResponseHanler,
    TextResponseHanler,
)
from example.tornado_example.security_route import (
    APIKeyCookieHanler,
    APIKeyHeaderHanler,
    APIKeyQueryHanler,
    OAuth2LoginHandler,
    OAuth2UserInfoHandler,
    OAuth2UserNameHandler,
    UserNameByHttpBasicCredentialsHandler,
    UserNameByHttpBearerHandler,
    UserNameByHttpDigestHandler,
)
from example.tornado_example.utils import MyHandler, global_pait
from pait.app.tornado import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.tornado.plugin.cache_response import CacheResponsePlugin
from pait.extra.config import MatchRule
from pait.field import Header, Json, Query
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar

user_pait: Pait = global_pait.create_sub_pait(group="user")
link_pait: Pait = global_pait.create_sub_pait(
    group="links",
    status=PaitStatus.release,
    tag=(tag.links_tag,),
)
other_pait: Pait = pait.create_sub_pait(author=("so1n",), status=PaitStatus.test, group="other")


class RaiseTipHandler(MyHandler):
    @other_pait(
        desc="test pait raise tip",
        status=PaitStatus.abandoned,
        tag=(tag.raise_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        content__type: str = Header.i(description="content-type"),
    ) -> None:
        """Test Method: error tip"""
        self.write({"code": 0, "msg": "", "data": {"content_type": content__type}})


class RaiseNotTipHandler(MyHandler):
    @other_pait(
        desc="test pait raise tip",
        status=PaitStatus.abandoned,
        tag=(tag.raise_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
        param_handler_plugin=NotTipAsyncParamHandler,
    )
    async def post(
        self,
        content__type: str = Header.i(description="content-type"),
    ) -> None:
        """Test Method: error tip"""
        self.write({"code": 0, "msg": "", "data": {"content_type": content__type}})


class CbvHandler(MyHandler):
    content_type: str = Header.i(alias="Content-Type")

    @user_pait(
        status=PaitStatus.release,
        tag=(tag.cbv_tag,),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Query.i(description="sex"),
        model: UserOtherModel = Query.i(raw_return=True),
    ) -> None:
        """Text Pydantic Model and Field"""
        self.write(
            {
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
        )

    @user_pait(
        desc="test cbv post method",
        tag=(tag.cbv_tag,),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        uid: int = Json.i(description="user id", gt=10, lt=1000),
        user_name: str = Json.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Json.i(description="sex"),
        model: UserOtherModel = Json.i(raw_return=True),
    ) -> None:
        self.write(
            {
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
        )


class NotPaitCbvHandler(MyHandler):
    user_name: str = Query.i()

    async def get(self) -> None:
        self.write(self.user_name)

    async def post(self) -> None:
        self.write(self.user_name)


class LoginHanlder(MyHandler):
    @link_pait(response_model_list=[LoginRespModel])
    async def post(
        self, uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
        )


class GetUserHandler(MyHandler):
    @link_pait(response_model_list=[SuccessRespModel])
    def get(
        self,
        token: str = Header.i(
            "",
            description="token",
            links=link_login_token_model,
            example=TemplateVar("token"),
        ),
    ) -> None:
        if token:
            self.write({"code": 0, "msg": ""})
        else:
            self.write({"code": 1, "msg": ""})


def add_api_doc_route(app: Application) -> None:
    """Split out to improve the speed of test cases"""
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc", app=app)
    add_doc_route(app, pin_code="6666", prefix="/", title="Pait Api Doc(private)")


def create_app() -> Application:
    app: Application = Application(
        [
            (r"/api/login", LoginHanlder),
            (r"/api/user", GetUserHandler),
            (r"/api/raise-tip", RaiseTipHandler),
            (r"/api/raise-not-tip", RaiseNotTipHandler),
            (r"/api/cbv", CbvHandler),
            (r"/api/not-pait-cbv", NotPaitCbvHandler),
            (r"/api/field/post", PostHandler),
            (r"/api/field/pait-base-field/(?P<age>\w+)", PaitBaseFieldHandler),
            (r"/api/field/field-default-factory", FieldDefaultFactoryHandler),
            (r"/api/field/same-alias", SameAliasHandler),
            (r"/api/field/pait-model", PaitModelHanler),
            (r"/api/resp/check-resp", CheckRespHandler),
            (r"/api/resp/text-resp", TextResponseHanler),
            (r"/api/resp/html-resp", HtmlResponseHanler),
            (r"/api/resp/file-resp", FileResponseHanler),
            (r"/api/plugin/auto-complete-json-plugin", AutoCompleteJsonHandler),
            (r"/api/plugin/cache-response", CacheResponseHandler),
            (r"/api/plugin/cache-response1", CacheResponse1Handler),
            (r"/api/plugin/check-json-plugin", CheckJsonPluginHandler),
            (r"/api/plugin/check-json-plugin-1", CheckJsonPlugin1Handler),
            (r"/api/plugin/mock/(?P<age>\w+)", MockHandler),
            (r"/api/plugin/at-most-one-of-by-extra-param", ParamAtMostOneOfByExtraParamHandler),
            (r"/api/plugin/at-most-one-of", ParamAtMostOneOfHandler),
            (r"/api/plugin/required-by-extra-param", ParamRequiredByExtraParamHandler),
            (r"/api/plugin/required", ParamRequiredHandler),
            (r"/api/depend/depend", DependHandler),
            (r"/api/depend/check-depend-contextmanager", DependContextmanagerHanler),
            (r"/api/depend/check-depend-async-contextmanager", DependAsyncContextmanagerHanler),
            (r"/api/depend/check-pre-depend-contextmanager", PreDependContextmanagerHanler),
            (r"/api/depend/check-pre-depend-async-contextmanager", PreDependAsyncContextmanagerHanler),
            (r"/api/security/api-key-cookie-route", APIKeyCookieHanler),
            (r"/api/security/api-key-header-route", APIKeyHeaderHanler),
            (r"/api/security/api-key-query-route", APIKeyQueryHanler),
            (r"/api/security/oauth2-login", OAuth2LoginHandler),
            (r"/api/security/oauth2-user-name", OAuth2UserNameHandler),
            (r"/api/security/oauth2-user-info", OAuth2UserInfoHandler),
            (r"/api/security/user-name-by-http-basic-credentials", UserNameByHttpBasicCredentialsHandler),
            (r"/api/security/user-name-by-http-bearer", UserNameByHttpBearerHandler),
            (r"/api/security/user-name-by-http-digest", UserNameByHttpDigestHandler),
        ]
    )
    CacheResponsePlugin.set_redis_to_app(app, redis=Redis(decode_responses=True))
    load_app(app, auto_load_route=True)
    return app


if __name__ == "__main__":
    import logging

    from pydantic import BaseModel

    from pait.extra.config import apply_block_http_method_set, apply_extra_openapi_model
    from pait.g import config

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
    app: Application = create_app()
    add_grpc_gateway_route(app)
    add_api_doc_route(app)
    app.listen(8000)
    app.settings["before_server_start"]()
    IOLoop.instance().start()
