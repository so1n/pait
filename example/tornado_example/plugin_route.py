import time
from typing import List, Optional

from redis.asyncio import Redis  # type: ignore
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
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.app.tornado.plugin import AtMostOneOfPlugin, RequiredPlugin
from pait.app.tornado.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.tornado.plugin.cache_resonse import CacheResponsePlugin
from pait.app.tornado.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.tornado.plugin.mock_response import MockPlugin
from pait.field import MultiQuery, Path, Query
from pait.model.response import HtmlResponseModel
from pait.model.status import PaitStatus

plugin_pait: Pait = global_pait.create_sub_pait(
    group="plugin",
    status=PaitStatus.release,
    tag=(tag.plugin_tag,),
)


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


class MockHandler(MyHandler):
    @plugin_pait(
        status=PaitStatus.release,
        append_tag=(tag.mock_tag, tag.user_tag),
        response_model_list=[UserSuccessRespModel2, FailRespModel],
        plugin_list=[MockPlugin.build()],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        email: str = Query.i(default="example@xxx.com", description="user email"),
        age: int = Path.i(description="age"),
        sex: SexEnum = Query.i(description="sex"),
        multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    ) -> None:
        """Test Field"""
        self.write(
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


class AutoCompleteJsonHandler(MyHandler):
    @plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
    async def get(self) -> dict:
        """Test json plugin by resp type is dict"""
        return {
            "code": 0,
            "msg": "",
            "data": {
                "image_list": [
                    {"aaa": 10},
                    {"aaa": "123"},
                ],
                # "uid": 0,
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


class CacheResponseHandler(MyHandler):
    @plugin_pait(
        response_model_list=[HtmlResponseModel, FailRespModel],
        post_plugin_list=[
            CacheResponsePlugin.build(
                redis=Redis(decode_responses=True),
                cache_time=10,
                include_exc=(RuntimeError,),
                enable_cache_name_merge_param=True,
            )
        ],
    )
    async def get(self, raise_exc: Optional[int] = Query.i(default=None)) -> None:
        timestamp_str = str(time.time())
        if raise_exc:
            if raise_exc == 1:
                raise Exception(timestamp_str)
            elif raise_exc == 2:
                raise RuntimeError(timestamp_str)
        else:
            self.write(timestamp_str)


class CacheResponse1Handler(MyHandler):
    @plugin_pait(
        response_model_list=[HtmlResponseModel],
        post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
    )
    async def get(self) -> None:
        self.write(str(time.time()))


class CheckJsonPluginHandler(MyHandler):
    @plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
    async def get(
        self,
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


class CheckJsonPlugin1Handler(MyHandler):
    @plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
    async def get(
        self,
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


class CheckParamHandler(MyHandler):
    @plugin_pait(
        tag=(tag.check_param_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
        post_plugin_list=[
            RequiredPlugin.build(required_dict={"birthday": ["alias_user_name"]}),
            AtMostOneOfPlugin.build(at_most_one_of_list=[["user_name", "alias_user_name"]]),
        ],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
        user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
        alias_user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
        age: int = Query.i(description="age", gt=1, lt=100),
        birthday: Optional[str] = Query.i(None, description="birthday"),
        sex: SexEnum = Query.i(description="sex"),
    ) -> None:
        """Test check param"""
        self.write(
            {
                "code": 0,
                "msg": "",
                "data": {
                    "birthday": birthday,
                    "uid": uid,
                    "user_name": user_name or alias_user_name,
                    "email": email,
                    "age": age,
                    "sex": sex.value,
                },
            }
        )


if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/check-param", CheckParamHandler),
                (r"/api/auto-complete-json-plugin", AutoCompleteJsonHandler),
                (r"/api/cache-response", CacheResponseHandler),
                (r"/api/cache-response1", CacheResponse1Handler),
                (r"/api/check-json-plugin", CheckJsonPluginHandler),
                (r"/api/check-json-plugin-1", CheckJsonPlugin1Handler),
                (r"/api/mock/(?P<age>\w+)", MockHandler),
            ]
        )
