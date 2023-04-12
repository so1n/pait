import time
from typing import List, Optional

from redis.asyncio import Redis  # type: ignore
from starlette.responses import JSONResponse, PlainTextResponse
from typing_extensions import TypedDict

from example.common import tag
from example.common.request_model import SexEnum
from example.common.response_model import (
    AutoCompleteRespModel,
    FailRespModel,
    SimpleRespModel,
    UserSuccessRespModel2,
    UserSuccessRespModel3,
)
from example.starlette_example.utils import create_app, global_pait
from pait.app.starlette import Pait
from pait.app.starlette.plugin import (
    AtMostOneOfExtraParam,
    AtMostOneOfPlugin,
    RequiredExtraParam,
    RequiredGroupExtraParam,
    RequiredPlugin,
)
from pait.app.starlette.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.starlette.plugin.cache_response import CacheResponsePlugin
from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.field import MultiQuery, Path, Query
from pait.model import PaitStatus, TextResponseModel

plugin_pait: Pait = global_pait.create_sub_pait(
    group="plugin",
    status=PaitStatus.release,
    tag=(tag.plugin_tag,),
)


@plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
async def async_auto_complete_json_route() -> dict:
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


@plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
def auto_complete_json_route() -> dict:
    """Test json plugin by resp type is dict"""
    return {
        "code": 0,
        "msg": "",
        # "uid": 0,
        "data": {
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
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> dict:
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
    return return_dict


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
async def async_check_json_plugin_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> dict:
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
    return return_dict


_sub_typed_dict = TypedDict(
    "_sub_typed_dict",
    {
        "uid": int,
        "user_name": str,
        "email": str,
    },
)
_typed_dict = TypedDict(
    "_typed_dict",
    {
        "code": int,
        "msg": str,
        "data": _sub_typed_dict,
    },
)


@plugin_pait(
    response_model_list=[TextResponseModel, FailRespModel],
    post_plugin_list=[
        CacheResponsePlugin.build(
            redis=Redis(decode_responses=True),
            cache_time=10,
            include_exc=(RuntimeError,),
            enable_cache_name_merge_param=True,
        )
    ],
)
async def cache_response(raise_exc: Optional[int] = Query.i(default=None)) -> PlainTextResponse:
    timestamp_str = str(time.time())
    if raise_exc:
        if raise_exc == 1:
            raise Exception(timestamp_str)
        elif raise_exc == 2:
            raise RuntimeError(timestamp_str)
    else:
        return PlainTextResponse(timestamp_str, 200)


@plugin_pait(
    response_model_list=[TextResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
)
async def cache_response1() -> PlainTextResponse:
    return PlainTextResponse(str(time.time()))


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
def check_json_plugin_route1(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> _typed_dict:
    """Test json plugin by resp type is typed dict"""
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
    return return_dict  # type: ignore


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
async def async_check_json_plugin_route1(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> _typed_dict:
    """Test json plugin by resp type is typed dict"""
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
    return return_dict  # type: ignore


@plugin_pait(
    status=PaitStatus.release,
    append_tag=(tag.mock_tag, tag.user_tag),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    plugin_list=[MockPlugin.build()],
)
def mock_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> JSONResponse:
    """Test gen mock response"""
    return JSONResponse(
        {
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
    )


@plugin_pait(
    status=PaitStatus.release,
    append_tag=(tag.mock_tag, tag.user_tag),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    plugin_list=[MockPlugin.build()],
)
async def async_mock_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> JSONResponse:
    """Test gen mock response"""
    return JSONResponse(
        {
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
    )


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        AtMostOneOfPlugin.build(
            at_most_one_of_list=[["user_name", "alias_user_name"], ["alias_user_name", "other_user_name"]]
        )
    ],
)
async def param_at_most_one_of_route(
    uid: int = Query.i(description="user id"),
    user_name: Optional[str] = Query.i(None, description="user name"),
    alias_user_name: Optional[str] = Query.i(None, description="user name"),
    other_user_name: Optional[str] = Query.i(None, description="user name"),
) -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name or alias_user_name or other_user_name,
            },
        }
    )


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[AtMostOneOfPlugin.build()],
)
async def param_at_most_one_of_route_by_extra_param(
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
) -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name or alias_user_name or other_user_name,
            },
        }
    )


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        RequiredPlugin.build(required_dict={"email": ["birthday"], "user_name": ["sex"]}),
    ],
)
async def param_required_route(
    uid: int = Query.i(description="user id"),
    email: Optional[str] = Query.i(None, description="user email"),
    birthday: Optional[str] = Query.i(None, description="birthday"),
    user_name: Optional[str] = Query.i(None, description="user name"),
    sex: Optional[SexEnum] = Query.i(None, description="sex"),
) -> JSONResponse:
    """Test check param"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {"birthday": birthday, "uid": uid, "email": email, "user_name": user_name, "sex": sex},
        }
    )


@plugin_pait(
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        RequiredPlugin.build(),
    ],
)
async def param_required_route_by_extra_param(
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
) -> JSONResponse:
    """Test check param"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {"birthday": birthday, "uid": uid, "email": email, "user_name": user_name, "sex": sex},
        }
    )


if __name__ == "__main__":
    with create_app() as app:
        CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
        app.add_route("/api/mock/{age}", mock_route, methods=["GET"])
        app.add_route("/api/async-mock/{age}", async_mock_route, methods=["GET"])
        app.add_route("/api/auto-complete-json-plugin", auto_complete_json_route, methods=["GET"])
        app.add_route("/api/async-auto-complete-json-plugin", async_auto_complete_json_route, methods=["GET"])
        app.add_route("/api/cache-response", cache_response, methods=["GET"])
        app.add_route("/api/cache-response1", cache_response1, methods=["GET"])
        app.add_route("/api/check-json-plugin", check_json_plugin_route, methods=["GET"])
        app.add_route("/api/check-json-plugin-1", check_json_plugin_route1, methods=["GET"])
        app.add_route("/api/async-check-json-plugin", async_check_json_plugin_route, methods=["GET"])
        app.add_route("/api/async-check-json-plugin-1", async_check_json_plugin_route1, methods=["GET"])
        app.add_route("/api/at-most-one-of-by-extra-param", param_at_most_one_of_route_by_extra_param, methods=["GET"])
        app.add_route("/api/at-most-one-of", param_at_most_one_of_route, methods=["GET"])
        app.add_route("/api/required-by-extra-param", param_required_route_by_extra_param, methods=["GET"])
        app.add_route("/api/required", param_required_route, methods=["GET"])
