from __future__ import annotations

import hashlib
import time
from tempfile import NamedTemporaryFile
from typing import Any, AsyncContextManager, Dict, List, Optional, Tuple

import aiofiles  # type: ignore
import grpc
from pydantic import ValidationError
from redis.asyncio import Redis  # type: ignore
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from typing_extensions import TypedDict

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.param_verify.common import tag
from example.param_verify.common.depend import AsyncGetUserDepend, async_context_depend, context_depend, demo_depend
from example.param_verify.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.param_verify.common.response_model import (
    AutoCompleteRespModel,
    FailRespModel,
    FileRespModel,
    HtmlRespModel,
    LoginRespModel,
    NotAuthenticatedTextRespModel,
    SimpleRespModel,
    SuccessRespModel,
    TextRespModel,
    UserSuccessRespModel,
    UserSuccessRespModel2,
    UserSuccessRespModel3,
    gen_response_model_handle,
    link_login_token_model,
)
from pait.app import set_app_attribute
from pait.app.starlette import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.starlette.grpc_route import GrpcGatewayRoute
from pait.app.starlette.plugin import AtMostOneOfPlugin
from pait.app.starlette.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.starlette.plugin.cache_resonse import CacheResponsePlugin
from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.app.starlette.security.api_key import api_key
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.extra.config import MatchRule
from pait.field import Cookie, Depends, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.model.response import TextResponseModel
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar
from pait.plugin.required import AsyncRequiredPlugin

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)

user_pait: Pait = global_pait.create_sub_pait(group="user")
check_resp_pait: Pait = global_pait.create_sub_pait(group="check_resp", tag=(tag.check_resp_tag,))
link_pait: Pait = global_pait.create_sub_pait(
    group="links",
    status=PaitStatus.release,
    tag=(tag.links_tag,),
)
plugin_pait: Pait = global_pait.create_sub_pait(
    group="plugin",
    status=PaitStatus.release,
    tag=(tag.plugin_tag,),
)
other_pait: Pait = pait.create_sub_pait(author=("so1n",), status=PaitStatus.test, group="other")


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return JSONResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, PaitBaseException):
        return JSONResponse({"code": -1, "msg": str(exc)})
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JSONResponse({"code": -1, "msg": f"miss param: {error_param_list}"})
    elif isinstance(exc, HTTPException):
        raise exc
    return JSONResponse({"code": -1, "msg": str(exc)})


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
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.post_tag),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def post_route(
    model: UserModel = Json.i(raw_return=True),
    other_model: UserOtherModel = Json.i(raw_return=True),
    sex: SexEnum = Json.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> JSONResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JSONResponse({"code": 0, "msg": "", "data": return_dict})


@user_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.depend_tag),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
    user_model: UserModel = Depends.i(AsyncGetUserDepend()),
) -> JSONResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
        }
    )


@user_pait(
    status=PaitStatus.release,
    tag=(tag.same_alias_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


@user_pait(
    status=PaitStatus.test,
    tag=(tag.field_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def field_default_factory_route(
    demo_value: int = Json.i(description="Json body value not empty"),
    data_list: List[str] = Json.i(default_factory=list, description="test default factory"),
    data_dict: Dict[str, Any] = Json.i(default_factory=dict, description="test default factory"),
) -> JSONResponse:
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}
    )


@user_pait(
    status=PaitStatus.release,
    tag=(tag.field_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def pait_base_field_route(
    upload_file: Any = File.i(description="upload file"),
    a: str = Form.i(description="form data"),
    b: str = Form.i(description="form data"),
    c: List[str] = MultiForm.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    sex: SexEnum = Query.i(description="sex"),
) -> JSONResponse:
    """Test the use of all BaseField-based"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "filename": upload_file.filename,
                "content": (await upload_file.read()).decode(),
                "form_a": a,
                "form_b": b,
                "form_c": c,
                "cookie": cookie,
                "multi_user_name": multi_user_name,
                "age": age,
                "uid": uid,
                "user_name": user_name,
                "email": email,
                "sex": sex,
            },
        }
    )


@user_pait(
    status=PaitStatus.release,
    tag=(tag.check_param_tag,),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    post_plugin_list=[
        AsyncRequiredPlugin.build(required_dict={"birthday": ["alias_user_name"]}),
        AtMostOneOfPlugin.build(at_most_one_of_list=[["user_name", "alias_user_name"]]),
    ],
)
async def check_param_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    alias_user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    birthday: Optional[str] = Query.i(None, description="birthday"),
    sex: SexEnum = Query.i(description="sex"),
) -> JSONResponse:
    """Test check param"""
    return JSONResponse(
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


@user_pait(
    group="user",
    status=PaitStatus.release,
    tag=(tag.check_resp_tag,),
    response_model_list=[UserSuccessRespModel3, FailRespModel],
)
async def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> JSONResponse:
    """Test test-helper check response"""
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
    return JSONResponse(return_dict)


@user_pait(
    status=PaitStatus.release,
    tag=(tag.mock_tag,),
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


@user_pait(
    status=PaitStatus.release,
    tag=(tag.mock_tag,),
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


@other_pait(status=PaitStatus.test, tag=(tag.field_tag,), response_model_list=[SimpleRespModel, FailRespModel])
async def pait_model_route(test_pait_model: TestPaitModel) -> JSONResponse:
    """Test pait model"""
    return JSONResponse({"code": 0, "msg": "", "data": test_pait_model.dict()})


@other_pait(status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_contextmanager_route(
    uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


@other_pait(
    status=PaitStatus.test,
    tag=(tag.depend_tag,),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@other_pait(
    status=PaitStatus.test,
    tag=(tag.depend_tag,),
    pre_depend_list=[async_context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_async_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@other_pait(tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_async_contextmanager_route(
    uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


class CbvRoute(HTTPEndpoint):
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
    ) -> JSONResponse:
        """Text cbv route get"""
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


@check_resp_pait(response_model_list=[TextRespModel])
async def async_text_response_route() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[TextRespModel])
def text_response_route() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[HtmlRespModel])
async def async_html_response_route() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[HtmlRespModel])
def html_response_route() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[FileRespModel])
def file_response_route() -> FileResponse:
    named_temporary_file = NamedTemporaryFile(delete=True)
    f: Any = named_temporary_file.__enter__()
    f.write("Hello Word!".encode())
    f.seek(0)

    def close_file() -> None:
        named_temporary_file.__exit__(None, None, None)

    response: FileResponse = FileResponse(
        f.name, media_type="application/octet-stream", background=BackgroundTask(close_file)
    )
    response.headers.append("X-Example-Type", "file")
    return response


@check_resp_pait(response_model_list=[FileRespModel])
async def async_file_response_route() -> FileResponse:
    named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
    f: Any = await named_temporary_file.__aenter__()
    await f.write("Hello Word!".encode())
    await f.seek(0)

    async def close_file() -> None:
        await named_temporary_file.__aexit__(None, None, None)

    response: FileResponse = FileResponse(
        f.name, media_type="application/octet-stream", background=BackgroundTask(close_file)
    )
    response.headers.append("X-Example-Type", "file")
    return response


@link_pait(response_model_list=[LoginRespModel])
def login_route(
    uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
) -> JSONResponse:
    # only use test
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


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


@plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
async def async_auto_complete_json_route() -> dict:
    """Test json plugin by resp type is dict"""
    return {
        "code": 0,
        "msg": "",
        "data": {
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
            ]
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


async def not_pait_route(user_name: str = Query.i()) -> PlainTextResponse:
    return PlainTextResponse(user_name)


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


@other_pait(
    status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, NotAuthenticatedTextRespModel]
)
def api_key_route(
    token: str = Depends.i(
        api_key(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        )
    )
) -> JSONResponse:
    return JSONResponse({"token": token})


def add_grpc_gateway_route(app: Starlette) -> None:
    """Split out to improve the speed of test cases"""
    from typing import Callable, Type
    from uuid import uuid4

    from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2
    from pait.util.grpc_inspect.stub import GrpcModel
    from pait.util.grpc_inspect.types import Message

    def _make_response(resp_dict: dict) -> Response:
        return JSONResponse({"code": 0, "msg": "", "data": resp_dict})

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:

            if grpc_model.method in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                async def _route(
                    request_pydantic_model: request_pydantic_model_class,  # type: ignore
                    token: str = Header.i(description="User Token"),
                    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                ) -> Any:
                    func: Callable = self.get_grpc_func(grpc_model.method)
                    request_dict: dict = request_pydantic_model.dict()  # type: ignore
                    if grpc_model.method == "/user.User/logout_user":
                        # logout user need token param
                        request_dict["token"] = token
                    else:
                        # check token
                        result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(
                            self.channel
                        ).get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                    # add req_id to request
                    grpc_msg: Message = await func(request_msg, metadata=[("req_id", req_id)])
                    return self._make_response(self.get_dict_from_msg(grpc_msg))

                return _route

    grpc_gateway_route: CustomerGrpcGatewayRoute = CustomerGrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        prefix="/api",
        title="Grpc",
        parse_msg_desc="by_mypy",
        gen_response_model_handle=gen_response_model_handle,
        make_response=_make_response,
    )
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest

    def _before_server_start(*_: Any) -> None:
        grpc_gateway_route.init_channel(grpc.aio.insecure_channel("0.0.0.0:9000"))

    async def _after_server_stop(*_: Any) -> None:
        await grpc_gateway_route.channel.close()

    app.add_event_handler("startup", _before_server_start)
    app.add_event_handler("shutdown", _after_server_stop)


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
            Route("/api/post", post_route, methods=["POST"]),
            Route("/api/depend", depend_route, methods=["POST"]),
            Route("/api/field-default-factory", field_default_factory_route, methods=["POST"]),
            Route("/api/pait-base-field/{age}", pait_base_field_route, methods=["POST"]),
            Route("/api/same-alias", same_alias_route, methods=["GET"]),
            Route("/api/mock/{age}", mock_route, methods=["GET"]),
            Route("/api/async-mock/{age}", async_mock_route, methods=["GET"]),
            Route("/api/pait-model", pait_model_route, methods=["POST"]),
            Route("/api/cbv", CbvRoute),
            Route("/api/check-param", check_param_route, methods=["GET"]),
            Route("/api/check-resp", check_response_route, methods=["GET"]),
            Route("/api/text-resp", text_response_route, methods=["GET"]),
            Route("/api/html-resp", html_response_route, methods=["GET"]),
            Route("/api/file-resp", file_response_route, methods=["GET"]),
            Route("/api/async-text-resp", async_text_response_route, methods=["GET"]),
            Route("/api/async-html-resp", async_html_response_route, methods=["GET"]),
            Route("/api/async-file-resp", async_file_response_route, methods=["GET"]),
            Route("/api/auto-complete-json-plugin", auto_complete_json_route, methods=["GET"]),
            Route("/api/async-auto-complete-json-plugin", async_auto_complete_json_route, methods=["GET"]),
            Route("/api/cache-response", cache_response, methods=["GET"]),
            Route("/api/cache-response1", cache_response1, methods=["GET"]),
            Route("/api/not-pait-route", not_pait_route, methods=["GET"]),
            Route("/api/not-pait-cbv", NotPaitCbvRoute),
            Route("/api/check-json-plugin", check_json_plugin_route, methods=["GET"]),
            Route("/api/check-json-plugin-1", check_json_plugin_route1, methods=["GET"]),
            Route("/api/async-check-json-plugin", async_check_json_plugin_route, methods=["GET"]),
            Route("/api/async-check-json-plugin-1", async_check_json_plugin_route1, methods=["GET"]),
            Route("/api/check_depend_contextmanager", depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_depend_async_contextmanager", depend_async_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_contextmanager", pre_depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_async_contextmanager", pre_depend_async_contextmanager_route, methods=["GET"]),
            Route("/api/security/api-key", api_key_route, methods=["GET"]),
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

    from pait.extra.config import apply_block_http_method_set, apply_extra_openapi_model
    from pait.g import config

    class ExtraModel(BaseModel):
        extra_a: str = Query.i(default="", description="Fields used to demonstrate the expansion module")
        extra_b: int = Query.i(default=0, description="Fields used to demonstrate the expansion module")

    config.init_config(
        apply_func_list=[
            apply_block_http_method_set({"HEAD", "OPTIONS"}),
            apply_extra_openapi_model(ExtraModel, match_rule=MatchRule(key="!tag", target="grpc")),
        ]
    )
    starltte_app: Starlette = create_app()
    add_grpc_gateway_route(starltte_app)
    add_api_doc_route(starltte_app)
    uvicorn.run(starltte_app, log_level="debug")
