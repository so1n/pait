from __future__ import annotations

import hashlib

from pydantic import ValidationError
from redis.asyncio import Redis  # type: ignore
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

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
from example.starlette_example.depend_route import (
    depend_async_contextmanager_route,
    depend_contextmanager_route,
    depend_route,
    pre_depend_async_contextmanager_route,
    pre_depend_contextmanager_route,
)
from example.starlette_example.field_route import (
    any_type_route,
    field_default_factory_route,
    pait_base_field_route,
    pait_model_route,
    post_route,
    same_alias_route,
)
from example.starlette_example.plugin_route import (
    async_auto_complete_json_route,
    async_check_json_plugin_route,
    async_mock_route,
    auto_complete_json_route,
    cache_response,
    cache_response1,
    check_json_plugin_route,
    mock_route,
    param_at_most_one_of_route,
    param_at_most_one_of_route_by_extra_param,
    param_required_route,
    param_required_route_by_extra_param,
    unified_html_response,
    unified_json_response,
    unified_text_response,
)
from example.starlette_example.response_route import (
    async_file_response_route,
    async_html_response_route,
    async_text_response_route,
    check_response_route,
    file_response_route,
    html_response_route,
    text_response_route,
)
from example.starlette_example.security_route import (
    api_key_cookie_route,
    api_key_header_route,
    api_key_query_route,
    get_user_name_by_http_basic_credentials,
    get_user_name_by_http_bearer,
    get_user_name_by_http_digest,
    oauth2_login,
    oauth2_user_info,
    oauth2_user_name,
)
from example.starlette_example.utils import api_exception, global_pait
from pait import _pydanitc_adapter
from pait.app.starlette import Pait, load_app, pait
from pait.app.starlette.plugin.cache_response import CacheResponsePlugin
from pait.exceptions import PaitBaseException
from pait.field import Header, Json, Query
from pait.g import config, pait_context
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar
from pait.openapi.doc_route import AddDocRoute, add_doc_route

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
async def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> JSONResponse:
    """Prompted error from pait when test does not find value"""
    return JSONResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    param_handler_plugin=NotTipAsyncParamHandler,
)
async def raise_not_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> JSONResponse:
    """Prompted error from pait when test does not find value"""
    return JSONResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


class CbvRoute(HTTPEndpoint):
    content_type: str = Header.i(alias="Content-Type")

    @user_pait(
        desc="Text cbv route get",
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
    ) -> JSONResponse:
        return JSONResponse(
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
    ) -> JSONResponse:
        """Text cbv route post"""
        return JSONResponse(
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


class NotPaitCbvRoute(HTTPEndpoint):
    user_name: str = Query.i()

    async def get(self) -> PlainTextResponse:
        return PlainTextResponse(self.user_name)

    async def post(self) -> PlainTextResponse:
        return PlainTextResponse(self.user_name)


@link_pait(response_model_list=[LoginRespModel])
def login_route(
    uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
) -> JSONResponse:
    # only use test
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


if _pydanitc_adapter.is_v1:

    @link_pait(response_model_list=[SuccessRespModel])
    def get_user_route(
        token: str = Header.i(
            "",
            description="token",
            links=link_login_token_model,
            example=TemplateVar("token"),
        )
    ) -> JSONResponse:
        if token:
            return JSONResponse({"code": 0, "msg": ""})
        else:
            return JSONResponse({"code": 1, "msg": ""})

else:

    @link_pait(response_model_list=[SuccessRespModel])
    def get_user_route(
        token: str = Header.i(
            "",
            description="token",
            json_schema_extra=lambda v: v.update(links=link_login_token_model, example=TemplateVar("token")),
        )
    ) -> JSONResponse:
        if token:
            return JSONResponse({"code": 0, "msg": ""})
        else:
            return JSONResponse({"code": 1, "msg": ""})


async def not_pait_route(user_name: str = Query.i()) -> PlainTextResponse:
    return PlainTextResponse(user_name)


@other_pait(tag=(tag.openapi_exclude_tag, tag.openapi_include_tag))
async def tag_route() -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "exclude": pait_context.get().pait_core_model.tag_label["exclude"],
                "include": pait_context.get().pait_core_model.tag_label["include"],
            },
        }
    )


def add_api_doc_route(app: Starlette) -> None:
    """Split out to improve the speed of test cases"""
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc", app=app)
    # prefix `/` route group must be behind other route group
    add_doc_route(app, pin_code="6666", prefix="/", title="Pait Api Doc(private)")


def create_app() -> Starlette:
    app: Starlette = Starlette(
        routes=[
            Route("/api/login", login_route, methods=["POST"]),
            Route("/api/user", get_user_route, methods=["GET"]),
            Route("/api/raise-tip", raise_tip_route, methods=["POST"]),
            Route("/api/raise-not-tip", raise_not_tip_route, methods=["POST"]),
            Route("/api/cbv", CbvRoute),
            Route("/api/not-pait", not_pait_route, methods=["GET"]),
            Route("/api/not-pait-cbv", NotPaitCbvRoute),
            Route("/api/tag", tag_route, methods=["GET"]),
            Route("/api/field/post", post_route, methods=["POST"]),
            Route("/api/field/pait-base-field/{age}", pait_base_field_route, methods=["POST"]),
            Route("/api/field/field-default-factory", field_default_factory_route, methods=["POST"]),
            Route("/api/field/same-alias", same_alias_route, methods=["GET"]),
            Route("/api/field/pait-model", pait_model_route, methods=["POST"]),
            Route("/api/field/any-type", any_type_route, methods=["POST"]),
            Route("/api/resp/check-resp", check_response_route, methods=["GET"]),
            Route("/api/resp/text-resp", text_response_route, methods=["GET"]),
            Route("/api/resp/html-resp", html_response_route, methods=["GET"]),
            Route("/api/resp/file-resp", file_response_route, methods=["GET"]),
            Route("/api/resp/async-text-resp", async_text_response_route, methods=["GET"]),
            Route("/api/resp/async-html-resp", async_html_response_route, methods=["GET"]),
            Route("/api/resp/async-file-resp", async_file_response_route, methods=["GET"]),
            Route("/api/plugin/unified-text-resp", unified_text_response, methods=["GET"]),
            Route("/api/plugin/unified-html-resp", unified_html_response, methods=["GET"]),
            Route("/api/plugin/unified-json-resp", unified_json_response, methods=["GET"]),
            Route("/api/plugin/mock/{age}", mock_route, methods=["GET"]),
            Route("/api/plugin/async-mock/{age}", async_mock_route, methods=["GET"]),
            Route("/api/plugin/auto-complete-json-plugin", auto_complete_json_route, methods=["GET"]),
            Route("/api/plugin/async-auto-complete-json-plugin", async_auto_complete_json_route, methods=["GET"]),
            Route("/api/plugin/cache-response", cache_response, methods=["GET"]),
            Route("/api/plugin/cache-response1", cache_response1, methods=["GET"]),
            Route("/api/plugin/check-json-plugin", check_json_plugin_route, methods=["GET"]),
            Route("/api/plugin/async-check-json-plugin", async_check_json_plugin_route, methods=["GET"]),
            Route(
                "/api/plugin/at-most-one-of-by-extra-param", param_at_most_one_of_route_by_extra_param, methods=["GET"]
            ),
            Route("/api/plugin/at-most-one-of", param_at_most_one_of_route, methods=["GET"]),
            Route("/api/plugin/required-by-extra-param", param_required_route_by_extra_param, methods=["GET"]),
            Route("/api/plugin/required", param_required_route, methods=["GET"]),
            Route("/api/depend/depend", depend_route, methods=["POST"]),
            Route("/api/depend/depend-contextmanager", depend_contextmanager_route, methods=["GET"]),
            Route("/api/depend/depend-async-contextmanager", depend_async_contextmanager_route, methods=["GET"]),
            Route("/api/depend/pre-depend-contextmanager", pre_depend_contextmanager_route, methods=["GET"]),
            Route(
                "/api/depend/pre-depend-async-contextmanager",
                pre_depend_async_contextmanager_route,
                methods=["GET"],
            ),
            Route("/api/security/api-cookie-key", api_key_cookie_route, methods=["GET"]),
            Route("/api/security/api-header-key", api_key_header_route, methods=["GET"]),
            Route("/api/security/api-query-key", api_key_query_route, methods=["GET"]),
            Route("/api/security/oauth2-login", oauth2_login, methods=["POST"]),
            Route("/api/security/oauth2-user-name", oauth2_user_name, methods=["GET"]),
            Route("/api/security/oauth2-user-info", oauth2_user_info, methods=["GET"]),
            Route(
                "/api/security/user-name-by-http-basic-credentials",
                get_user_name_by_http_basic_credentials,
                methods=["GET"],
            ),
            Route("/api/security/user-name-by-http-bearer", get_user_name_by_http_bearer, methods=["GET"]),
            Route("/api/security/user-name-by-http-digest", get_user_name_by_http_digest, methods=["GET"]),
        ]
    )
    CacheResponsePlugin.set_redis_to_app(app, redis=Redis(decode_responses=True))

    app.add_exception_handler(PaitBaseException, api_exception)
    app.add_exception_handler(ValidationError, api_exception)
    app.add_exception_handler(RuntimeError, api_exception)
    load_app(app, auto_load_route=True)
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore
    from pydantic import BaseModel

    from pait.extra.config import apply_block_http_method_set

    class ExtraModel(BaseModel):
        extra_a: str = Query.i(default="", description="Fields used to demonstrate the expansion module")
        extra_b: int = Query.i(default=0, description="Fields used to demonstrate the expansion module")

    config.init_config(
        apply_func_list=[
            apply_block_http_method_set({"HEAD", "OPTIONS"}),
        ]
    )
    starlette_app: Starlette = create_app()
    add_api_doc_route(starlette_app)
    uvicorn.run(starlette_app, log_level="debug")
