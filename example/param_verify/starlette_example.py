from __future__ import annotations

import time
from typing import Any, AsyncContextManager, List, Optional, Tuple

import aiofiles  # type: ignore
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route

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
from pait.app.starlette import add_doc_route, pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"code": -1, "msg": str(exc)})


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
) -> JSONResponse:
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JSONResponse({"code": 0, "msg": "", "data": return_dict})


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
) -> JSONResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JSONResponse({"code": 0, "msg": "", "data": return_dict})


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
) -> JSONResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return_dict = model.dict()
    return_dict.update({"user_agent": depend_tuple[0], "age": depend_tuple[1]})
    return JSONResponse({"code": 0, "msg": "", "data": return_dict})


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
) -> JSONResponse:
    """Test Field"""
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
) -> JSONResponse:
    """Test Field"""
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
    birthday: str = Query.i(None, description="birthday"),
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel3, FailRespModel],
    at_most_one_of_list=[["user_name", "alias_user_name"]],
    required_by={"birthday": ["alias_user_name"]},
)
async def test_check_resp(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> JSONResponse:
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
    return JSONResponse(return_dict)


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
)
def test_same_alias(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> JSONResponse:
    return JSONResponse({"query_token": query_token, "header_token": header_token})


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
) -> JSONResponse:
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
            },
        }
    )


@pait(
    author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[UserSuccessRespModel, FailRespModel]
)
async def test_pait_model(test_model: TestPaitModel) -> JSONResponse:
    """Test Field"""
    return JSONResponse({"code": 0, "msg": "", "data": test_model.dict()})


class TestCbv(HTTPEndpoint):
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
    ) -> JSONResponse:
        """Text Pydantic Model and Field"""
        return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": model.age}
        return JSONResponse({"code": 0, "msg": "", "data": return_dict})

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
    ) -> JSONResponse:
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({"user_agent": self.user_agent})
        return JSONResponse({"code": 0, "msg": "", "data": return_dict})


@pait(author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[SuccessRespModel])
async def test_depend_contextmanager(
    uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel],
)
async def test_pre_depend_contextmanager(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@pait(author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[SuccessRespModel])
async def test_depend_async_contextmanager(
    uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    pre_depend_list=[async_context_depend],
    response_model_list=[SuccessRespModel],
)
async def test_pre_depend_async_contextmanager(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[TextRespModel],
)
async def test_text_response() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[HtmlRespModel],
)
async def test_html_response() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[FileRespModel],
)
async def test_file_response() -> FileResponse:
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


def create_app() -> Starlette:

    app: Starlette = Starlette(
        routes=[
            Route("/api/get/{age}", test_get, methods=["GET"]),
            Route("/api/mock/{age}", test_mock, methods=["GET"]),
            Route("/api/check_param", test_check_param, methods=["GET"]),
            Route("/api/check_resp", test_check_resp, methods=["GET"]),
            Route("/api/post", test_post, methods=["POST"]),
            Route("/api/depend", test_depend, methods=["POST"]),
            Route("/api/other_field", test_other_field, methods=["POST"]),
            Route("/api/same_alias", test_same_alias, methods=["GET"]),
            Route("/api/raise_tip", test_raise_tip, methods=["POST"]),
            Route("/api/cbv", TestCbv),
            Route("/api/text_resp", test_text_response, methods=["GET"]),
            Route("/api/html_resp", test_html_response, methods=["GET"]),
            Route("/api/file_resp", test_file_response, methods=["GET"]),
            Route("/api/pait_model", test_pait_model, methods=["POST"]),
            Route("/api/check_depend_contextmanager", test_depend_contextmanager, methods=["GET"]),
            Route("/api/check_depend_async_contextmanager", test_depend_async_contextmanager, methods=["GET"]),
            Route("/api/check_pre_depend_contextmanager", test_pre_depend_contextmanager, methods=["GET"]),
            Route("/api/check_pre_depend_async_contextmanager", test_pre_depend_async_contextmanager, methods=["GET"]),
        ]
    )
    add_doc_route(app)
    app.add_exception_handler(PaitBaseException, api_exception)
    app.add_exception_handler(ValidationError, api_exception)
    app.add_exception_handler(RuntimeError, api_exception)
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(create_app(), log_level="debug")
