from __future__ import annotations

import time
from typing import Any, AsyncContextManager, List, Optional, Tuple

import aiofiles  # type: ignore
from pydantic import ValidationError
from sanic import response
from sanic.app import Sanic
from sanic.request import Request
from sanic.views import HTTPMethodView

from example.param_verify.model import (
    FailRespModel,
    FileRespModel,
    HtmlRespModel,
    SexEnum,
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
from pait.app.sanic import add_doc_route, pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus

test_filename: str = ""


async def api_exception(request: Request, exc: Exception) -> response.HTTPResponse:
    return response.json({"code": -1, "msg": str(exc)})


@pait(
    author=("so1n",),
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=("test",),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def test_raise_tip(
    model: UserModel = Body.i(),
    other_model: UserOtherModel = Body.i(),
    content_type: str = Header.i(description="content-type"),
) -> response.HTTPResponse:
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return response.json({"code": 0, "msg": "", "data": return_dict})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "post"),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def test_post(
    model: UserModel = Body.i(),
    other_model: UserOtherModel = Body.i(),
    sex: SexEnum = Body.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="content-type"),
) -> response.HTTPResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return response.json({"code": 0, "msg": "", "data": return_dict})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "depend"),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def test_depend(
    request: Request,
    model: UserModel = Query.i(),
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
) -> response.HTTPResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return_dict = model.dict()
    return_dict.update({"user_agent": depend_tuple[0], "age": depend_tuple[1]})
    return response.json({"code": 0, "msg": "", "data": return_dict})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
)
async def test_get(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    age: int = Path.i(description="age"),
    sex: SexEnum = Query.i(description="sex"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
) -> response.HTTPResponse:
    """Test Field"""
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    enable_mock_response=True,
)
async def test_mock(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: str = Query.i(default="example@xxx.com", description="user email"),
    age: int = Path.i(description="age"),
    sex: SexEnum = Query.i(description="sex"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
) -> response.HTTPResponse:
    """Test Field"""
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    at_most_one_of_list=[["user_name", "alias_user_name"]],
    required_by={"birthday": ["alias_user_name"]},
)
async def test_check_param(
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel3, FailRespModel],
)
async def test_check_resp(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> response.HTTPResponse:
    """Test check param"""
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
)
def test_same_alias(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> response.HTTPResponse:
    return response.json({"query_token": query_token, "header_token": header_token})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
)
async def test_other_field(
    upload_file: Any = File.i(description="upload file"),
    a: str = Form.i(description="form data"),
    b: str = Form.i(description="form data"),
    c: List[str] = MultiForm.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie"),
) -> response.HTTPResponse:
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
            },
        }
    )


@pait(
    author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[UserSuccessRespModel, FailRespModel]
)
async def test_pait_model(test_model: TestPaitModel) -> response.HTTPResponse:
    """Test Field"""
    return response.json({"code": 0, "msg": "", "data": test_model.dict()})


class TestCbv(HTTPMethodView):
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
    ) -> response.HTTPResponse:
        """Text Pydantic Model and Field"""
        return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": model.age}
        return response.json({"code": 0, "msg": "", "data": return_dict})

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
    ) -> response.HTTPResponse:
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({"user_agent": self.user_agent})
        return response.json({"code": 0, "msg": "", "data": return_dict})


@pait(author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[SuccessRespModel, FailRespModel])
async def test_depend_contextmanager(
    uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def test_pre_depend_contextmanager(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    pre_depend_list=[async_context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def test_pre_depend_async_contextmanager(is_raise: bool = Query.i(default=False)) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": ""})


@pait(author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[SuccessRespModel, FailRespModel])
async def test_depend_async_contextmanager(
    uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)
) -> response.HTTPResponse:
    if is_raise:
        raise RuntimeError()
    return response.json({"code": 0, "msg": uid})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[TextRespModel],
)
async def test_text_response(request: Request) -> response.HTTPResponse:
    return response.text(str(time.time()), headers={"X-Example-Type": "text"})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[HtmlRespModel],
)
async def test_html_response(request: Request) -> response.HTTPResponse:
    return response.text(
        "<H1>" + str(time.time()) + "</H1>", headers={"X-Example-Type": "html"}, content_type="text/html"
    )


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[FileRespModel],
)
async def test_file_response(request: Request) -> response.StreamingHTTPResponse:
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


def create_app() -> Sanic:
    app: Sanic = Sanic(name="pait")
    add_doc_route(app)
    app.add_route(test_get, "/api/get/<age>", methods={"GET"})
    app.add_route(test_mock, "/api/mock/<age>", methods={"GET"})
    app.add_route(test_check_param, "/api/check_param", methods={"GET"})
    app.add_route(test_check_resp, "/api/check_resp", methods={"GET"})
    app.add_route(test_post, "/api/post", methods={"POST"})
    app.add_route(test_depend, "/api/depend", methods={"POST"})
    app.add_route(test_other_field, "/api/other_field", methods={"POST"})
    app.add_route(test_same_alias, "/api/same_alias", methods={"GET"})
    app.add_route(test_raise_tip, "/api/raise_tip", methods={"POST"})
    app.add_route(TestCbv.as_view(), "/api/cbv")
    app.add_route(test_pait_model, "/api/pait_model", methods={"POST"})
    app.add_route(test_text_response, "/api/text_resp", methods={"GET"})
    app.add_route(test_html_response, "/api/html_resp", methods={"GET"})
    app.add_route(test_file_response, "/api/file_resp", methods={"GET"})
    app.add_route(test_depend_contextmanager, "/api/check_depend_contextmanager", methods={"GET"})
    app.add_route(test_pre_depend_contextmanager, "/api/check_pre_depend_contextmanager", methods={"GET"})
    app.add_route(test_depend_async_contextmanager, "/api/check_depend_async_contextmanager", methods={"GET"})
    app.add_route(test_pre_depend_async_contextmanager, "/api/check_pre_depend_async_contextmanager", methods={"GET"})
    app.exception(PaitBaseException)(api_exception)
    app.exception(ValidationError)(api_exception)
    app.exception(RuntimeError)(api_exception)
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(create_app(), log_level="debug")
