import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from django.views import View

from example.common import tag
from example.common.request_model import SexEnum, UserOtherModel
from example.common.response_model import FailRespModel, SimpleRespModel, UserSuccessRespModel
from example.common.utils import NotTipParamHandler
from example.django_example.api_route import main_api_route
from example.django_example.depend_route import (
    depend_contextmanager_route,
    depend_route,
    pre_depend_contextmanager_route,
    pre_depend_route,
)
from example.django_example.field_route import (
    any_type_route,
    field_default_factory_route,
    pait_base_field_route,
    pait_model_route,
    post_route,
    query_route,
    same_alias_route,
)
from example.django_example.file_route import multipart_route, stream_for_data_route
from example.django_example.mcp_route import (
    add_mcp_demo_route,
    mcp_depend_route,
    mcp_http_dispatcher_route,
    mcp_private_route,
    mcp_response_route,
    mcp_upsert_user_route,
    mcp_user_route,
    mcp_user_summary_route,
)
from example.django_example.plugin_route import (
    auto_complete_json_route,
    cache_response,
    cache_response1,
    check_json_plugin_route,
    mock_route,
    param_at_most_onf_of_route,
    param_at_most_onf_of_route_by_extra_param,
    param_required_route,
    param_required_route_by_extra_param,
    unified_html_response,
    unified_json_response,
    unified_text_response,
)
from example.django_example.response_route import (
    check_response_route,
    file_response_route,
    html_response_route,
    text_response_route,
)
from example.django_example.security_route import (
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
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.base.simple_route import SimpleRoute
from pait.app.django import Pait, add_simple_route, load_app, pait
from pait.field import Header, Json, Query
from pait.g import get_ctx
from pait.model.status import PaitStatus
from pait.openapi.doc_route import AddDocRoute, add_doc_route

other_pait: Pait = pait.create_sub_pait(author=("so1n",), status=PaitStatus.test, group="other")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),
) -> JsonResponse:
    """Prompted error from pait when test does not find value"""
    return JsonResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    param_handler_plugin=NotTipParamHandler,
)
def raise_not_tip_route(
    content__type: str = Header.i(description="Content-Type"),
) -> JsonResponse:
    """Prompted error from pait when test does not find value"""
    return JsonResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    tip_exception_class=None,
)
def new_raise_not_tip_route(
    content__type: str = Header.i(description="Content-Type"),
) -> JsonResponse:
    """Prompted error from pait when test does not find value"""
    return JsonResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


class CbvRoute(View):
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
    ) -> JsonResponse:
        """Text cbv route get"""
        return JsonResponse(
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
    def post(
        self,
        uid: int = Json.i(description="user id", gt=10, lt=1000),
        user_name: str = Json.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Json.i(description="sex"),
        model: UserOtherModel = Json.i(raw_return=True),
    ) -> JsonResponse:
        """Text cbv route post"""
        return JsonResponse(
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


@pait()
def simple_route() -> dict:
    return {"framework": "django", "simple": True}


@other_pait(tag=(tag.openapi_exclude_tag, tag.openapi_include_tag))
def tag_route() -> JsonResponse:
    return JsonResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "exclude": get_ctx().pait_core_model.tag_label["exclude"],
                "include": get_ctx().pait_core_model.tag_label["include"],
            },
        }
    )


urlpatterns = [
    route_path("api/raise-tip", raise_tip_route, ["POST"], name="raise_tip"),
    route_path("api/raise-not-tip", raise_not_tip_route, ["POST"], name="raise_not_tip"),
    route_path("api/new-raise-not-tip", new_raise_not_tip_route, ["POST"], name="new_raise_not_tip"),
    route_path("api/cbv", CbvRoute.as_view(), ["GET", "POST"], name="cbv"),
    route_path("api/tag", tag_route, ["GET"], name="tag"),
    route_path("api/field/post", post_route, ["POST"], name="field_post"),
    route_path("api/field/query", query_route, ["GET"], name="field_query"),
    route_path(
        "api/field/pait-base-field/<int:age>",
        pait_base_field_route,
        ["POST"],
        name="field_pait_base_field",
    ),
    route_path(
        "api/field/field-default-factory",
        field_default_factory_route,
        ["POST"],
        name="field_default_factory",
    ),
    route_path("api/field/same-alias", same_alias_route, ["GET"], name="field_same_alias"),
    route_path("api/field/pait-model", pait_model_route, ["POST"], name="field_pait_model"),
    route_path("api/field/any-type", any_type_route, ["POST"], name="field_any_type"),
    route_path("api/resp/text-resp", text_response_route, ["GET"], name="resp_text"),
    route_path("api/resp/html-resp", html_response_route, ["GET"], name="resp_html"),
    route_path("api/resp/file-resp", file_response_route, ["GET"], name="resp_file"),
    route_path("api/resp/check-resp", check_response_route, ["GET"], name="resp_check"),
    route_path(
        "api/plugin/unified-html-response",
        unified_html_response,
        ["GET"],
        name="plugin_unified_html",
    ),
    route_path(
        "api/plugin/unified-text-response",
        unified_text_response,
        ["GET"],
        name="plugin_unified_text",
    ),
    route_path(
        "api/plugin/unified-json-response",
        unified_json_response,
        ["GET"],
        name="plugin_unified_json",
    ),
    route_path("api/plugin/mock/<int:age>", mock_route, ["GET"], name="plugin_mock"),
    route_path("api/plugin/check-json-plugin", check_json_plugin_route, ["GET"], name="plugin_check_json"),
    route_path("api/plugin/cache-response", cache_response, ["GET"], name="plugin_cache"),
    route_path("api/plugin/cache-response-1", cache_response1, ["GET"], name="plugin_cache_1"),
    route_path(
        "api/plugin/auto-complete-json-plugin",
        auto_complete_json_route,
        ["GET"],
        name="plugin_auto_complete",
    ),
    route_path(
        "api/plugin/at-most-one-of-by-extra-param",
        param_at_most_onf_of_route_by_extra_param,
        ["GET"],
        name="plugin_at_most_one_of_extra",
    ),
    route_path("api/plugin/at-most-one-of", param_at_most_onf_of_route, ["GET"], name="plugin_at_most_one_of"),
    route_path(
        "api/plugin/required-by-extra-param",
        param_required_route_by_extra_param,
        ["GET"],
        name="plugin_required_extra",
    ),
    route_path("api/plugin/required", param_required_route, ["GET"], name="plugin_required"),
    route_path("api/depend", depend_route, ["POST"], name="depend"),
    route_path("api/pre-depend", pre_depend_route, ["POST"], name="pre_depend"),
    route_path(
        "api/depend/depend-contextmanager",
        depend_contextmanager_route,
        ["GET"],
        name="depend_contextmanager",
    ),
    route_path(
        "api/depend/pre-depend-contextmanager",
        pre_depend_contextmanager_route,
        ["GET"],
        name="pre_depend_contextmanager",
    ),
    route_path("api/security/api-cookie-key", api_key_cookie_route, ["GET"], name="security_api_cookie_key"),
    route_path("api/security/api-header-key", api_key_header_route, ["GET"], name="security_api_header_key"),
    route_path("api/security/api-query-key", api_key_query_route, ["GET"], name="security_api_query_key"),
    route_path("api/security/oauth2-login", oauth2_login, ["POST"], name="security_oauth2_login"),
    route_path("api/security/oauth2-user-name", oauth2_user_name, ["GET"], name="security_oauth2_user_name"),
    route_path("api/security/oauth2-user-info", oauth2_user_info, ["GET"], name="security_oauth2_user_info"),
    route_path(
        "api/security/user-name-by-http-basic-credentials",
        get_user_name_by_http_basic_credentials,
        ["GET"],
        name="security_http_basic",
    ),
    route_path(
        "api/security/user-name-by-http-bearer",
        get_user_name_by_http_bearer,
        ["GET"],
        name="security_http_bearer",
    ),
    route_path(
        "api/security/user-name-by-http-digest",
        get_user_name_by_http_digest,
        ["GET"],
        name="security_http_digest",
    ),
    route_path("api/file/stream-for-data", stream_for_data_route, ["POST"], name="file_stream_for_data"),
    route_path("api/file/multipart", multipart_route, ["POST"], name="file_multipart"),
    route_path("api/mcp/user/<int:uid>", mcp_user_route, ["GET"], name="mcp_user"),
    route_path("api/mcp/user-summary/<int:uid>", mcp_user_summary_route, ["GET"], name="mcp_user_summary"),
    route_path("api/mcp/user", mcp_upsert_user_route, ["POST"], name="mcp_upsert_user"),
    route_path("api/mcp/response", mcp_response_route, ["GET"], name="mcp_response"),
    route_path(
        "api/mcp/http-dispatcher",
        mcp_http_dispatcher_route,
        ["GET"],
        name="mcp_http_dispatcher",
    ),
    route_path("api/mcp/depend", mcp_depend_route, ["GET"], name="mcp_depend"),
    route_path("api/mcp/private", mcp_private_route, ["GET"], name="mcp_private"),
]
main_api_route.inject(urlpatterns)
add_simple_route(urlpatterns, SimpleRoute(methods=["GET"], url="/api/simple", route=simple_route))
add_mcp_demo_route(urlpatterns)


def load_example_app() -> dict:
    return load_app(urlpatterns, overwrite_already_exists_data=True)


def create_app() -> List[Any]:
    app = list(urlpatterns)
    return app


def add_api_doc_route() -> None:
    add_doc_route(urlpatterns, pin_code="6666", prefix="/", title="Pait Api Doc(private)")
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc", app=urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.main_example")
