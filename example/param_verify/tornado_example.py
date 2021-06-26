from __future__ import annotations

from typing import Any, List, Tuple

from tornado.httputil import RequestStartLine
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from example.param_verify.model import (
    FailRespModel,
    SexEnum,
    TestPaitModel,
    UserModel,
    UserOtherModel,
    UserSuccessRespModel,
    UserSuccessRespModel2,
    demo_depend,
)
from pait.app.tornado import add_doc_route, pait
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus


class MyHandler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        self.write({"exc": str(exc)})
        self.finish()


class RaiseTipHandler(MyHandler):
    @pait(
        author=("so1n",),
        desc="test pait raise tip",
        status=PaitStatus.abandoned,
        tag=("test",),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        model: UserModel = Body.i(),
        other_model: UserOtherModel = Body.i(),
        content_type: str = Header.i(description="content-type"),
    ) -> None:
        """Test Method: error tip"""
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({"content_type": content_type})
        self.write({"code": 0, "msg": "", "data": return_dict})


class TestPostHandler(MyHandler):
    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "post"),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        model: UserModel = Body.i(),
        other_model: UserOtherModel = Body.i(),
        sex: SexEnum = Body.i(description="sex"),
        content_type: str = Header.i(alias="Content-Type", description="content-type"),
    ) -> None:
        """Test Method:Post Pydantic Model"""
        return_dict = model.dict()
        return_dict["sex"] = sex.value
        return_dict.update(other_model.dict())
        return_dict.update({"content_type": content_type})
        self.write({"code": 0, "msg": "", "data": return_dict})


class TestDependHandler(MyHandler):
    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "depend"),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        request: RequestStartLine,
        model: UserModel = Query.i(),
        depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
    ) -> None:
        """Test Method:Post request, Pydantic Model"""
        assert request is not None, "Not found request"
        return_dict = model.dict()
        return_dict.update({"user_agent": depend_tuple[0], "age": depend_tuple[1]})
        self.write({"code": 0, "msg": "", "data": return_dict})


class TestGetHandler(MyHandler):
    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "get"),
        response_model_list=[UserSuccessRespModel2, FailRespModel],
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


class TestOtherFieldHandler(MyHandler):
    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "get"),
    )
    async def post(
        self,
        upload_file: Any = File.i(description="upload file"),
        a: str = Form.i(description="form data"),
        b: str = Form.i(description="form data"),
        c: List[str] = MultiForm.i(description="form data"),
        cookie: dict = Cookie.i(raw_return=True, description="cookie"),
    ) -> None:
        self.write(
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
                },
            }
        )


class TestPaitModelHanler(MyHandler):
    @pait(
        author=("so1n",),
        status=PaitStatus.test,
        tag=("test",),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(self, test_model: TestPaitModel) -> None:
        """Test Field"""
        self.write({"code": 0, "msg": "", "data": test_model.dict()})


class TestCbvHandler(MyHandler):
    user_agent: str = Header.i(alias="user-agent", description="ua")  # remove key will raise error

    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "get"),
        response_model_list=[UserSuccessRespModel2, FailRespModel],
    )
    async def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        email: str = Query.i(default="example@xxx.com", description="user email"),
        model: UserOtherModel = Query.i(),
    ) -> None:
        """Text Pydantic Model and Field"""
        return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": model.age}
        self.write({"code": 0, "msg": "", "data": return_dict})

    @pait(
        author=("so1n",),
        desc="test cbv post method",
        group="user",
        tag=("user", "post"),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        model: UserModel = Body.i(),
        other_model: UserOtherModel = Body.i(),
    ) -> None:
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({"user_agent": self.user_agent})
        self.write({"code": 0, "msg": "", "data": return_dict})


def create_app() -> Application:
    app: Application = Application(
        [
            (r"/api/get/(?P<age>\w+)", TestGetHandler),
            (r"/api/post", TestPostHandler),
            (r"/api/depend", TestDependHandler),
            (r"/api/other_field", TestOtherFieldHandler),
            (r"/api/raise_tip", RaiseTipHandler),
            (r"/api/cbv", TestCbvHandler),
            (r"/api/pait_model", TestPaitModelHanler),
        ]
    )
    add_doc_route(app)
    return app


if __name__ == "__main__":
    create_app().listen(8000)
    IOLoop.instance().start()
