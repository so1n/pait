from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any, AsyncContextManager, Dict, List, Optional, Tuple

import aiofiles  # type: ignore
from pydantic import ValidationError
from redis.asyncio import Redis  # type: ignore
from sanic import response
from sanic.app import Sanic
from sanic.request import Request
from sanic.views import HTTPMethodView
from typing_extensions import TypedDict

from example.param_verify import tag
from example.param_verify.model import (
    FailRespModel,
    FileRespModel,
    HtmlRespModel,
    LoginRespModel,
    SexEnum,
    SimpleRespModel,
    SuccessRespModel,
    TestPaitModel,
    TextRespModel,
    UserModel,
    UserOtherModel,
    UserSuccessRespModel,
    UserSuccessRespModel2,
    UserSuccessRespModel3,
    async_context_depend,
    context_depend,
    demo_depend,
)
from pait.app.sanic import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.sanic.grpc_route import GrpcGatewayRoute
from pait.app.sanic.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.sanic.plugin.cache_resonse import CacheResponsePlugin
from pait.app.sanic.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.sanic.plugin.mock_response import MockPlugin
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.core import MatchRule
from pait.model.links import LinksModel
from pait.model.response import PaitTextResponseModel
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar
from pait.plugin.at_most_one_of import AtMostOneOfPlugin
from pait.plugin.required import RequiredPlugin
from pait.util.grpc_inspect.message_to_pydantic import grpc_timestamp_int_handler

test_filename: str = ""

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


async def api_exception(request: Request, exc: Exception) -> response.HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return response.json({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, PaitBaseException):
        return response.json({"code": -1, "msg": str(exc)})
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return response.json({"code": -1, "msg": f"miss param: {error_param_list}"})
    return response.json({"code": -1, "msg": str(exc)})


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> dict:
    """Prompted error from pait when test does not find value"""
    return {"code": 0, "msg": "", "data": {"content_type": content__type}}


@user_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.post_tag),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def post_route(
    model: UserModel = Body.i(raw_return=True),
    other_model: UserOtherModel = Body.i(raw_return=True),
    sex: SexEnum = Body.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> response.HTTPResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return response.json({"code": 0, "msg": "", "data": return_dict})


@other_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.depend_tag),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
) -> response.HTTPResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return response.json({"code": 0, "msg": "", "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1]}})


@other_pait(
    status=PaitStatus.release,
    tag=(tag.same_alias_tag,),
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


@user_pait(
    status=PaitStatus.test,
    tag=(tag.field_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def field_default_factory_route(
    demo_value: int = Body.i(description="Json body value not empty"),
    data_list: List[str] = Body.i(default_factory=list, description="test default factory"),
    data_dict: Dict[str, Any] = Body.i(default_factory=dict, description="test default factory"),
) -> response.HTTPResponse:
    return response.json(
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
) -> response.HTTPResponse:
    """Test the use of all BaseField-based"""
    return response.json(
        {
            "code": 0,
            "msg": "",
            "data": {
                "filename": upload_file.name,
                "content": upload_file.body.decode(),
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
        RequiredPlugin.build(required_dict={"birthday": ["alias_user_name"]}),
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
) -> response.HTTPResponse:
    """Test check param"""
    return response.json(
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
) -> response.HTTPResponse:
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
    return response.json(return_dict)


@user_pait(
    status=PaitStatus.release,
    tag=(tag.mock_tag,),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    plugin_list=[MockPlugin.build()],
)
async def mock_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> response.HTTPResponse:
    """Test gen mock response"""
    return response.json(
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
async def pait_model_route(test_pait_model: TestPaitModel) -> response.HTTPResponse:
    """Test pait model"""
    return response.json({"code": 0, "msg": "", "data": test_pait_model.dict()})


@other_pait(status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_contextmanager_route(
    uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


@other_pait(
    status=PaitStatus.test,
    tag=(tag.depend_tag,),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


@other_pait(
    status=PaitStatus.test,
    tag=(tag.depend_tag,),
    pre_depend_list=[async_context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_async_contextmanager_route(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


@other_pait(status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_async_contextmanager_route(
    uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


class CbvRoute(HTTPMethodView):
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
    ) -> response.HTTPResponse:
        """Text cbv route get"""
        return response.json(
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
        uid: int = Body.i(description="user id", gt=10, lt=1000),
        user_name: str = Body.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Body.i(description="sex"),
        model: UserOtherModel = Body.i(raw_return=True),
    ) -> response.HTTPResponse:
        """Text cbv route post"""
        return response.json(
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


class NotPaitCbvRoute(HTTPMethodView):
    user_name: str = Query.i()

    async def get(self) -> response.HTTPResponse:
        return response.text(self.user_name, 200)

    async def post(self) -> response.HTTPResponse:
        return response.text(self.user_name, 200)


@check_resp_pait(response_model_list=[TextRespModel])
async def text_response_route(request: Request) -> response.HTTPResponse:
    return response.text(str(time.time()), headers={"X-Example-Type": "text"})


@check_resp_pait(response_model_list=[HtmlRespModel])
async def html_response_route(request: Request) -> response.HTTPResponse:
    return response.text(
        "<H1>" + str(time.time()) + "</H1>", headers={"X-Example-Type": "html"}, content_type="text/html"
    )


@check_resp_pait(response_model_list=[FileRespModel])
async def file_response_route(request: Request) -> response.StreamingHTTPResponse:
    # sanic file response will return read file when `return resp`

    named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
    f: Any = await named_temporary_file.__aenter__()
    await f.write("Hello Word!".encode())
    await f.seek(0)
    resp: response.StreamingHTTPResponse = await response.file_stream(f.name, mime_type="application/octet-stream")
    resp.headers.add("X-Example-Type", "file")

    raw_streaming_fn = resp.streaming_fn

    async def _streaming_fn(_response: response.BaseHTTPResponse) -> None:
        await raw_streaming_fn(_response)
        await named_temporary_file.__aexit__(None, None, None)

    resp.streaming_fn = _streaming_fn
    return resp


@link_pait(response_model_list=[LoginRespModel])
def login_route(
    uid: str = Body.i(description="user id"), password: str = Body.i(description="password")
) -> response.HTTPResponse:
    # only use test
    return response.json(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


token_links_Model = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


@link_pait(response_model_list=[SuccessRespModel])
def get_user_route(
    token: str = Header.i("", description="token", link=token_links_Model, example=TemplateVar("token"))
) -> response.HTTPResponse:
    if token:
        return response.json({"code": 0, "msg": ""})
    else:
        return response.json({"code": 1, "msg": ""})


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[AutoCompleteJsonRespPlugin.build()])
async def auto_complete_json_route(
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


@plugin_pait(
    response_model_list=[PaitTextResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(redis=Redis(decode_responses=True), cache_time=10)],
)
async def cache_response(request: Request) -> response.HTTPResponse:
    return response.text(str(time.time()))


@plugin_pait(
    response_model_list=[PaitTextResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
)
async def cache_response1(request: Request) -> response.HTTPResponse:
    return response.text(str(time.time()))


async def not_pait_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
) -> response.HTTPResponse:
    return response.text(str(uid), 200)


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
async def check_json_plugin_route(
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
async def check_json_plugin_route1(
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


def create_app() -> Sanic:
    app: Sanic = Sanic(name=__name__)
    CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
    add_doc_route(app, pin_code="6666", prefix="/", title="Pait Api Doc(private)")

    # grpc will use the current channel directly when initializing the channel,
    # so you need to initialize the event loop first and then initialize the grpc channel.
    from example.example_grpc.client import aio_manager_stub, aio_social_stub, aio_user_stub

    GrpcGatewayRoute(
        app,
        aio_user_stub,
        aio_social_stub,
        aio_manager_stub,
        prefix="/api",
        title="Grpc",
        grpc_timestamp_handler_tuple=(int, grpc_timestamp_int_handler),
    )
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc").gen_route(app)
    app.add_route(login_route, "/api/login", methods={"POST"})
    app.add_route(get_user_route, "/api/user", methods={"GET"})
    app.add_route(raise_tip_route, "/api/raise_tip", methods={"POST"})
    app.add_route(post_route, "/api/post", methods={"POST"})
    app.add_route(depend_route, "/api/depend", methods={"POST"})
    app.add_route(field_default_factory_route, "/api/field-default-factory", methods={"POST"})
    app.add_route(pait_base_field_route, "/api/pait-base-field/<age>", methods={"POST"})
    app.add_route(same_alias_route, "/api/same-alias", methods={"GET"})
    app.add_route(mock_route, "/api/mock/<age>", methods={"GET"})
    app.add_route(pait_model_route, "/api/pait-model", methods={"POST"})
    app.add_route(CbvRoute.as_view(), "/api/cbv")
    app.add_route(NotPaitCbvRoute.as_view(), "/api/not-pait-cbv")
    app.add_route(check_param_route, "/api/check-param", methods={"GET"})
    app.add_route(check_response_route, "/api/check-resp", methods={"GET"})
    app.add_route(text_response_route, "/api/text-resp", methods={"GET"})
    app.add_route(html_response_route, "/api/html-resp", methods={"GET"})
    app.add_route(file_response_route, "/api/file-resp", methods={"GET"})
    app.add_route(cache_response, "/api/cache-response", methods={"GET"})
    app.add_route(cache_response1, "/api/cache-response1", methods={"GET"})
    app.add_route(not_pait_route, "/api/not-pait", methods={"GET"})
    app.add_route(check_json_plugin_route, "/api/check-json-plugin", methods={"GET"})
    app.add_route(auto_complete_json_route, "/api/auto-complete-json-plugin", methods={"GET"})
    app.add_route(check_json_plugin_route1, "/api/check-json-plugin-1", methods={"GET"})
    app.add_route(depend_contextmanager_route, "/api/check-depend-contextmanager", methods={"GET"})
    app.add_route(pre_depend_contextmanager_route, "/api/check-pre-depend-contextmanager", methods={"GET"})
    app.add_route(depend_async_contextmanager_route, "/api/check-depend-async-contextmanager", methods={"GET"})
    app.add_route(pre_depend_async_contextmanager_route, "/api/check-pre-depend-async-contextmanager", methods={"GET"})
    app.exception(PaitBaseException)(api_exception)
    app.exception(ValidationError)(api_exception)
    app.exception(RuntimeError)(api_exception)
    load_app(app, auto_load_route=True)
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore
    from pydantic import BaseModel
    from uvicorn.config import Config
    from uvicorn.server import Server

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

    # grpc will use the current channel directly when initializing the channel,
    # so you need to initialize the event loop first and then initialize the grpc channel.

    async def main() -> None:
        uvicorn_config: Config = Config(create_app(), log_level="debug")
        await Server(uvicorn_config).serve()

        uvicorn.run(create_app(), log_level="debug")

    asyncio.run(main())
