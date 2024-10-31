import time
from typing import List, Optional

from flask import Response, jsonify, make_response
from redis.client import Redis  # type: ignore

from example.common import tag
from example.common.request_model import SexEnum
from example.common.response_model import (
    AutoCompleteRespModel,
    FailRespModel,
    SimpleRespModel,
    UserSuccessRespModel2,
    UserSuccessRespModel3,
)
from example.flask_example.utils import api_exception, create_app, global_pait
from pait.app.flask import Pait
from pait.app.flask.plugin import (
    AtMostOneOfExtraParam,
    AtMostOneOfPlugin,
    RequiredExtraParam,
    RequiredGroupExtraParam,
    RequiredPlugin,
)
from pait.app.flask.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.flask.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.app.flask.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.flask.plugin.mock_response import MockPlugin
from pait.app.flask.plugin.unified_response import UnifiedResponsePlugin
from pait.field import MultiQuery, Path, Query
from pait.model import response as pait_response
from pait.model.status import PaitStatus

plugin_pait: Pait = global_pait.create_sub_pait(
    group="plugin",
    status=PaitStatus.release,
    tag=(tag.plugin_tag,),
)


@plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
def auto_complete_json_route() -> dict:
    """Test json plugin by resp type is dict"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            # "uid": 0,
            "image_list": [
                {"aaa": 10},
                {"aaa": "123"},
            ],
            "music_list": [
                {
                    "name": "music1",
                    "url": "http://music1.com",
                    "singer": "singer1",
                },
                {
                    # "name": "music1",
                    "url": "http://music1.com",
                    # "singer": "singer1",
                },
            ],
        },
    }


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
def check_json_plugin_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> Response:
    """Test json plugin by resp type is dict"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return jsonify(return_dict)


@plugin_pait(
    response_model_list=[pait_response.HtmlResponseModel, FailRespModel],
    post_plugin_list=[
        CacheResponsePlugin.build(
            redis=Redis(decode_responses=True),
            cache_time=10,
            include_exc=(RuntimeError,),
            enable_cache_name_merge_param=True,
        )
    ],
)
def cache_response(raise_exc: Optional[int] = Query.i(default=None)) -> Response:
    timestamp_str = str(time.time())
    if raise_exc:
        if raise_exc == 1:
            raise Exception(timestamp_str)
        elif raise_exc == 2:
            raise RuntimeError(timestamp_str)
    return make_response(timestamp_str, 200)


@plugin_pait(
    response_model_list=[pait_response.HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
def cache_response1(key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()) -> Response:
    return make_response(str(time.time()), 200)


@plugin_pait(
    status=PaitStatus.release,
    append_tag=(tag.mock_tag, tag.user_tag),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    plugin_list=[MockPlugin.build()],
)
def mock_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test gen mock response"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
            "age": age,
            "sex": sex.value,
            "multi_user_name": multi_user_name,
        },
    }


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        AtMostOneOfPlugin.build(
            at_most_one_of_list=[["user_name", "alias_user_name"], ["other_user_name", "alias_user_name"]]
        )
    ],
)
def param_at_most_onf_of_route(
    uid: int = Query.i(description="user id"),
    user_name: Optional[str] = Query.i(None, description="user name"),
    alias_user_name: Optional[str] = Query.i(None, description="user name"),
    other_user_name: Optional[str] = Query.i(None, description="user name"),
) -> dict:
    return {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name or alias_user_name or other_user_name,
        },
    }


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[AtMostOneOfPlugin.build()],
)
def param_at_most_onf_of_route_by_extra_param(
    uid: int = Query.i(description="user id"),
    user_name: Optional[str] = Query.i(
        None, description="user name", extra_param_list=[AtMostOneOfExtraParam(group="user_name")]
    ),
    alias_user_name: Optional[str] = Query.i(
        None,
        description="user name",
        extra_param_list=[AtMostOneOfExtraParam(group="user_name"), AtMostOneOfExtraParam(group="alias_user_name")],
    ),
    other_user_name: Optional[str] = Query.i(
        None, description="user name", extra_param_list=[AtMostOneOfExtraParam(group="alias_user_name")]
    ),
) -> dict:
    return {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name or alias_user_name or other_user_name,
        },
    }


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        RequiredPlugin.build(required_dict={"email": ["birthday"], "user_name": ["sex"]}),
    ],
)
def param_required_route(
    uid: int = Query.i(description="user id"),
    email: Optional[str] = Query.i(None, description="user email"),
    birthday: Optional[str] = Query.i(None, description="birthday"),
    user_name: Optional[str] = Query.i(None, description="user name"),
    sex: Optional[SexEnum] = Query.i(None, description="sex"),
) -> dict:
    """Test check param"""
    return {
        "code": 0,
        "msg": "",
        "data": {"birthday": birthday, "uid": uid, "email": email, "user_name": user_name, "sex": sex},
    }


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        RequiredPlugin.build(),
    ],
)
def param_required_route_by_extra_param(
    uid: int = Query.i(description="user id"),
    email: Optional[str] = Query.i(None, description="user email"),
    birthday: Optional[str] = Query.i(
        None, description="birthday", extra_param_list=[RequiredExtraParam(main_column="email")]
    ),
    user_name: Optional[str] = Query.i(
        None, description="user name", extra_param_list=[RequiredGroupExtraParam(group="user_name", is_main=True)]
    ),
    sex: Optional[SexEnum] = Query.i(
        None, description="sex", extra_param_list=[RequiredGroupExtraParam(group="user_name")]
    ),
) -> dict:
    """Test check param"""
    return {
        "code": 0,
        "msg": "",
        "data": {"birthday": birthday, "uid": uid, "email": email, "user_name": user_name, "sex": sex},
    }


@plugin_pait(
    plugin_list=[UnifiedResponsePlugin.build()],
    response_model_list=[pait_response.HtmlResponseModel],
)
def unified_html_response() -> str:
    return "<html>Demo</html>"


@plugin_pait(
    plugin_list=[UnifiedResponsePlugin.build()],
    response_model_list=[pait_response.TextResponseModel],
)
def unified_text_response() -> str:
    return "Demo"


@plugin_pait(
    plugin_list=[UnifiedResponsePlugin.build()],
    response_model_list=[pait_response.JsonResponseModel],
)
def unified_json_response() -> dict:
    return {"data": "Demo"}


if __name__ == "__main__":
    with create_app(__name__) as app:
        CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
        app.add_url_rule("/api/check-json-plugin", view_func=check_json_plugin_route, methods=["GET"])
        app.add_url_rule("/api/cache-response", view_func=cache_response, methods=["GET"])
        app.add_url_rule("/api/cache-response-1", view_func=cache_response1, methods=["GET"])
        app.add_url_rule("/api/auto-complete-json-plugin", view_func=auto_complete_json_route, methods=["GET"])
        app.add_url_rule("/api/mock/<age>", view_func=mock_route, methods=["GET"])
        app.add_url_rule(
            "/api/at-most-one-of-by-extra-param", view_func=param_at_most_onf_of_route_by_extra_param, methods=["GET"]
        )
        app.add_url_rule("/api/at-most-one-of", view_func=param_at_most_onf_of_route, methods=["GET"])
        app.add_url_rule("/api/required-by-extra-param", view_func=param_required_route_by_extra_param, methods=["GET"])
        app.add_url_rule("/api/required", view_func=param_required_route, methods=["GET"])
        app.add_url_rule("/api/unified-html-response", view_func=unified_html_response, methods=["GET"])
        app.add_url_rule("/api/unified-text-response", view_func=unified_text_response, methods=["GET"])
        app.add_url_rule("/api/unified-json-response", view_func=unified_json_response, methods=["GET"])
        app.errorhandler(Exception)(api_exception)
