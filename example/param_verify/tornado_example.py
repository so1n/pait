from __future__ import annotations

import hashlib
import time
from typing import Dict, List, Optional, Tuple

import aiofiles  # type: ignore
from tornado.httputil import RequestStartLine
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
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
from pait.app.tornado import Pait, add_doc_route, pait
from pait.app.tornado.plugin.check_json_resp import AsyncCheckJsonRespPlugin
from pait.app.tornado.plugin.mock_response import MockPlugin
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.links import LinksModel
from pait.model.status import PaitStatus
from pait.plugin import PluginManager
from pait.plugin.at_most_one_of import AsyncAtMostOneOfPlugin
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


class MyHandler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
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
        content_type: str = Header.i(description="content-type"),
    ) -> None:
        """Test Method: error tip"""
        self.write({"code": 0, "msg": "", "data": {"content_type": content_type}})


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
            PluginManager(AsyncRequiredPlugin, required_dict={"birthday": ["alias_user_name"]}),
            PluginManager(AsyncAtMostOneOfPlugin, at_most_one_of_list=[["user_name", "alias_user_name"]]),
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
        plugin_list=[PluginManager(MockPlugin)],
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
    def get(self, token: str = Header.i("", description="token", link=token_links_Model)) -> None:
        if token:
            self.write({"code": 0, "msg": ""})
        else:
            self.write({"code": 1, "msg": ""})


class CheckJsonPluginHandler(MyHandler):
    @plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[PluginManager(AsyncCheckJsonRespPlugin)])
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
    @plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[PluginManager(AsyncCheckJsonRespPlugin)])
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


def create_app() -> Application:
    app: Application = Application(
        [
            (r"/api/login", LoginHanlder),
            (r"/api/user", GetUserHandler),
            (r"/api/raise-tip", RaiseTipHandler),
            (r"/api/post", PostHandler),
            (r"/api/depend", DependHandler),
            (r"/api/pait-base-field/(?P<age>\w+)", PaitBaseFieldHandler),
            (r"/api/same-alias", SameAliasHandler),
            (r"/api/mock/(?P<age>\w+)", MockHandler),
            (r"/api/pait-model", PaitModelHanler),
            (r"/api/cbv", CbvHandler),
            (r"/api/check-param", CheckParamHandler),
            (r"/api/check-resp", CheckRespHandler),
            (r"/api/text-resp", TextResponseHanler),
            (r"/api/html-resp", HtmlResponseHanler),
            (r"/api/file-resp", FileResponseHanler),
            (r"/api/check-json-plugin", CheckJsonPluginHandler),
            (r"/api/check-json-plugin-1", CheckJsonPlugin1Handler),
            (r"/api/check-depend-contextmanager", DependContextmanagerHanler),
            (r"/api/check-depend-async-contextmanager", DependAsyncContextmanagerHanler),
            (r"/api/check-pre-depend-contextmanager", PreDependContextmanagerHanler),
            (r"/api/check-pre-depend-async-contextmanager", PreDependAsyncContextmanagerHanler),
        ]
    )
    add_doc_route(app)
    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.DEBUG
    )
    create_app().listen(8000)
    IOLoop.instance().start()
