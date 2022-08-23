from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

import aiofiles  # type: ignore
import grpc
from pydantic import ValidationError
from redis.asyncio import Redis  # type: ignore
from tornado.httputil import RequestStartLine
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from typing_extensions import TypedDict

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.param_verify import tag
from example.param_verify.model import (
    AutoCompleteRespModel,
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
    gen_response_model_handle,
)
from pait.app import set_app_attribute
from pait.app.tornado import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.tornado.grpc_route import GrpcGatewayRoute
from pait.app.tornado.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.tornado.plugin.cache_resonse import CacheResponsePlugin
from pait.app.tornado.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.tornado.plugin.mock_response import MockPlugin
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.core import MatchRule
from pait.model.links import LinksModel
from pait.model.response import PaitHtmlResponseModel
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar
from pait.plugin.at_most_one_of import AtMostOneOfPlugin
from pait.plugin.required import RequiredPlugin

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


class MyHandler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, PaitBaseParamException):
            self.write({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
        elif isinstance(exc, PaitBaseException):
            self.write({"code": -1, "msg": str(exc)})
        elif isinstance(exc, ValidationError):
            error_param_list: list = []
            for i in exc.errors():
                error_param_list.extend(i["loc"])
            self.write({"code": -1, "msg": f"miss param: {error_param_list}"})
        else:
            self.write({"code": -1, "msg": str(exc)})
        self.finish()


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


class PostHandler(MyHandler):
    @user_pait(
        status=PaitStatus.release,
        tag=(tag.user_tag, tag.post_tag),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        model: UserModel = Body.i(raw_return=True),
        other_model: UserOtherModel = Body.i(raw_return=True),
        sex: SexEnum = Body.i(description="sex"),
        content_type: str = Header.i(alias="Content-Type", description="content-type"),
    ) -> None:
        """Test Method:Post Pydantic Model"""
        return_dict = model.dict()
        return_dict["sex"] = sex.value
        return_dict.update(other_model.dict())
        return_dict.update({"content_type": content_type})
        self.write({"code": 0, "msg": "", "data": return_dict})


class DependHandler(MyHandler):
    @other_pait(
        status=PaitStatus.release,
        tag=(tag.user_tag, tag.depend_tag),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        request: RequestStartLine,
        depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
    ) -> None:
        """Test Method:Post request, Pydantic Model"""
        assert request is not None, "Not found request"
        self.write({"code": 0, "msg": "", "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1]}})


class SameAliasHandler(MyHandler):
    @other_pait(
        status=PaitStatus.release,
        tag=(tag.same_alias_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    def get(
        self, query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
    ) -> None:
        self.write({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


class FieldDefaultFactoryHandler(MyHandler):
    @user_pait(
        status=PaitStatus.test,
        tag=(tag.field_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        demo_value: int = Body.i(description="Json body value not empty"),
        data_list: List[str] = Body.i(default_factory=list, description="test default factory"),
        data_dict: Dict[str, Any] = Body.i(default_factory=dict, description="test default factory"),
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}
        )


class PaitBaseFieldHandler(MyHandler):
    @user_pait(
        status=PaitStatus.release,
        tag=(tag.field_tag,),
        response_model_list=[SimpleRespModel, FailRespModel],
    )
    async def post(
        self,
        upload_file: Dict = File.i(raw_return=True, description="upload file"),
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
    ) -> None:
        self.write(
            {
                "code": 0,
                "msg": "",
                "data": {
                    "filename": list(upload_file.values())[0]["filename"],
                    "content": list(upload_file.values())[0]["body"].decode(),
                    "form_a": a,
                    "form_b": b,
                    "form_c": c,
                    "cookie": {key: key for key, _ in cookie.items()},
                    "multi_user_name": multi_user_name,
                    "age": age,
                    "uid": uid,
                    "user_name": user_name,
                    "email": email,
                    "sex": sex,
                },
            }
        )


class CheckParamHandler(MyHandler):
    @user_pait(
        status=PaitStatus.release,
        tag=(tag.check_param_tag,),
        response_model_list=[UserSuccessRespModel2, FailRespModel],
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


class CheckRespHandler(MyHandler):
    @user_pait(
        status=PaitStatus.release,
        tag=(tag.check_resp_tag,),
        response_model_list=[UserSuccessRespModel3, FailRespModel],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        age: int = Query.i(description="age", gt=1, lt=100),
        display_age: int = Query.i(0, description="display_age"),
    ) -> None:
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
        self.write(return_dict)


class MockHandler(MyHandler):
    @user_pait(
        group="user",
        status=PaitStatus.release,
        tag=(tag.mock_tag,),
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


class PaitModelHanler(MyHandler):
    @other_pait(status=PaitStatus.release, tag=(tag.field_tag,), response_model_list=[SimpleRespModel, FailRespModel])
    async def post(self, test_model: TestPaitModel) -> None:
        """Test pait model"""
        self.write({"code": 0, "msg": "", "data": test_model.dict()})


class DependContextmanagerHanler(MyHandler):
    @other_pait(tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
    async def get(self, uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": uid})


class DependAsyncContextmanagerHanler(MyHandler):
    @other_pait(tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
    async def get(self, uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": uid})


class PreDependContextmanagerHanler(MyHandler):
    @other_pait(
        tag=(tag.depend_tag,), pre_depend_list=[context_depend], response_model_list=[SuccessRespModel, FailRespModel]
    )
    async def get(self, is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": ""})


class PreDependAsyncContextmanagerHanler(MyHandler):
    @other_pait(
        tag=(tag.depend_tag,),
        pre_depend_list=[async_context_depend],
        response_model_list=[SuccessRespModel, FailRespModel],
    )
    async def get(self, is_raise: bool = Query.i(default=False)) -> None:
        if is_raise:
            raise RuntimeError()
        self.write({"code": 0, "msg": ""})


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
        uid: int = Body.i(description="user id", gt=10, lt=1000),
        user_name: str = Body.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Body.i(description="sex"),
        model: UserOtherModel = Body.i(raw_return=True),
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


class TextResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[TextRespModel])
    async def get(self) -> None:
        self.write(str(time.time()))
        self.set_header("X-Example-Type", "text")
        self.set_header("Content-Type", "text/plain")


class HtmlResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[HtmlRespModel])
    async def get(self) -> None:
        self.write("<H1>" + str(time.time()) + "</H1>")
        self.set_header("X-Example-Type", "html")
        self.set_header("Content-Type", "text/html")


class FileResponseHanler(MyHandler):
    @check_resp_pait(response_model_list=[FileRespModel])
    async def get(self) -> None:
        async with aiofiles.tempfile.NamedTemporaryFile() as f:  # type: ignore
            await f.write("Hello Word!".encode())
            await f.seek(0)
            async for line in f:
                self.write(line)

        self.set_header("X-Example-Type", "file")
        self.set_header("Content-Type", "application/octet-stream")


class LoginHanlder(MyHandler):
    @link_pait(response_model_list=[LoginRespModel])
    async def post(
        self, uid: str = Body.i(description="user id"), password: str = Body.i(description="password")
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
        )


token_links_Model = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


class GetUserHandler(MyHandler):
    @link_pait(response_model_list=[SuccessRespModel])
    def get(
        self, token: str = Header.i("", description="token", link=token_links_Model, example=TemplateVar("token"))
    ) -> None:
        if token:
            self.write({"code": 0, "msg": ""})
        else:
            self.write({"code": 1, "msg": ""})


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
        response_model_list=[PaitHtmlResponseModel, FailRespModel],
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
        response_model_list=[PaitHtmlResponseModel],
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


def add_grpc_gateway_route(app: Application) -> None:
    """Split out to improve the speed of test cases"""
    from sys import modules
    from typing import Callable, Type
    from uuid import uuid4

    from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2
    from pait.app.tornado.grpc_route import Self
    from pait.util.grpc_inspect.stub import GrpcModel
    from pait.util.grpc_inspect.types import Message

    def _tornado_make_response(resp_dict: dict) -> dict:
        return {"code": 0, "msg": "", "data": resp_dict}

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:

            if grpc_model.method in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                async def _route(
                    route_self: Self,
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
                        result: user_pb2.GetUidByTokenResult = await user_pb2_grpc.UserStub(
                            self.channel
                        ).get_uid_by_token(user_pb2.GetUidByTokenRequest(token=token))
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                    # add req_id to request
                    grpc_msg: Message = await func(request_msg, metadata=[("req_id", req_id)])
                    resp_dict: dict = self._make_response(self.get_dict_from_msg(grpc_msg))
                    route_self.write(resp_dict)

                # request_pydantic_model_class is not generated by this module,
                # so you need to inject request_pydantic_model_class into this module.
                modules[_route.__module__].__dict__["Self"] = Self
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
        make_response=_tornado_make_response,
    )
    grpc_gateway_route.with_request(MyHandler)
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest

    def _before_server_start() -> None:
        grpc_gateway_route.init_channel(grpc.aio.insecure_channel("0.0.0.0:9000"))

    app.settings["before_server_start"] = _before_server_start


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
            (r"/api/post", PostHandler),
            (r"/api/depend", DependHandler),
            (r"/api/field-default-factory", FieldDefaultFactoryHandler),
            (r"/api/pait-base-field/(?P<age>\w+)", PaitBaseFieldHandler),
            (r"/api/same-alias", SameAliasHandler),
            (r"/api/mock/(?P<age>\w+)", MockHandler),
            (r"/api/pait-model", PaitModelHanler),
            (r"/api/cbv", CbvHandler),
            (r"/api/not-pait-cbv", NotPaitCbvHandler),
            (r"/api/check-param", CheckParamHandler),
            (r"/api/check-resp", CheckRespHandler),
            (r"/api/text-resp", TextResponseHanler),
            (r"/api/html-resp", HtmlResponseHanler),
            (r"/api/file-resp", FileResponseHanler),
            (r"/api/auto-complete-json-plugin", AutoCompleteJsonHandler),
            (r"/api/cache-response", CacheResponseHandler),
            (r"/api/cache-response1", CacheResponse1Handler),
            (r"/api/check-json-plugin", CheckJsonPluginHandler),
            (r"/api/check-json-plugin-1", CheckJsonPlugin1Handler),
            (r"/api/check-depend-contextmanager", DependContextmanagerHanler),
            (r"/api/check-depend-async-contextmanager", DependAsyncContextmanagerHanler),
            (r"/api/check-pre-depend-contextmanager", PreDependContextmanagerHanler),
            (r"/api/check-pre-depend-async-contextmanager", PreDependAsyncContextmanagerHanler),
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
