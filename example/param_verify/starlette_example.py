from __future__ import annotations

import hashlib
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
from pait.app.starlette import add_doc_route, pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.model.links import LinksModel
from pait.model.status import PaitStatus


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"code": -1, "msg": str(exc)})


@pait(
    author=("so1n",),
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=("raise",),
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> JSONResponse:
    """Prompted error from pait when test does not find value"""
    return JSONResponse({"code": 0, "msg": "", "data": {"content_type": content__type}})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "post"),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
async def post_route(
    model: UserModel = Body.i(raw_return=True),
    other_model: UserOtherModel = Body.i(raw_return=True),
    sex: SexEnum = Body.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
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
    response_model_list=[SimpleRespModel, FailRespModel],
)
async def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
) -> JSONResponse:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return JSONResponse({"code": 0, "msg": "", "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1]}})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("same alias",),
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("field",),
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("check param",),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    at_most_one_of_list=[["user_name", "alias_user_name"]],
    required_by={"birthday": ["alias_user_name"]},
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("check response",),
    response_model_list=[UserSuccessRespModel3, FailRespModel],
)
async def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("mock",),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    enable_mock_response=True,
)
async def mock_route(
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


@pait(author=("so1n",), status=PaitStatus.test, tag=("field",), response_model_list=[SimpleRespModel, FailRespModel])
async def pait_model_route(test_pait_model: TestPaitModel) -> JSONResponse:
    """Test pait model"""
    return JSONResponse({"code": 0, "msg": "", "data": test_pait_model.dict()})


@pait(author=("so1n",), status=PaitStatus.test, tag=("depend",), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_contextmanager_route(
    uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("depend",),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("depend",),
    pre_depend_list=[async_context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
async def pre_depend_async_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": ""})


@pait(author=("so1n",), status=PaitStatus.test, tag=("depend",), response_model_list=[SuccessRespModel, FailRespModel])
async def depend_async_contextmanager_route(
    uid: str = Depends.i(async_context_depend), is_raise: bool = Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


class CbvRoute(HTTPEndpoint):
    content_type: str = Header.i(alias="Content-Type")

    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("cbv",),
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

    @pait(
        author=("so1n",),
        desc="test cbv post method",
        group="user",
        tag=("cbv",),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    async def post(
        self,
        uid: int = Body.i(description="user id", gt=10, lt=1000),
        user_name: str = Body.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Body.i(description="sex"),
        model: UserOtherModel = Body.i(raw_return=True),
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


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("check response",),
    response_model_list=[TextRespModel],
)
async def text_response_route() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("check response",),
    response_model_list=[HtmlRespModel],
)
async def html_response_route() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("check response",),
    response_model_list=[FileRespModel],
)
async def file_response_route() -> FileResponse:
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


@pait(
    author=("so1n",),
    status=PaitStatus.release,
    tag=("links",),
    response_model_list=[LoginRespModel],
)
def login_route(
    uid: str = Body.i(description="user id"), password: str = Body.i(description="password")
) -> JSONResponse:
    # only use test
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


token_links_Model = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


@pait(
    author=("so1n",),
    status=PaitStatus.release,
    tag=("links",),
    response_model_list=[SuccessRespModel],
)
def get_user_route(token: str = Header.i("", description="token", link=token_links_Model)) -> JSONResponse:
    if token:
        return JSONResponse({"code": 0, "msg": ""})
    else:
        return JSONResponse({"code": 1, "msg": ""})


def create_app() -> Starlette:

    app: Starlette = Starlette(
        routes=[
            Route("/api/login", login_route, methods=["POST"]),
            Route("/api/user", get_user_route, methods=["GET"]),
            Route("/api/raise-tip", raise_tip_route, methods=["POST"]),
            Route("/api/post", post_route, methods=["POST"]),
            Route("/api/depend", depend_route, methods=["POST"]),
            Route("/api/pait-base-field/{age}", pait_base_field_route, methods=["GET"]),
            Route("/api/same-alias", same_alias_route, methods=["GET"]),
            Route("/api/mock/{age}", mock_route, methods=["GET"]),
            Route("/api/pait-model", pait_model_route, methods=["POST"]),
            Route("/api/cbv", CbvRoute),
            Route("/api/check-param", check_param_route, methods=["GET"]),
            Route("/api/check-resp", check_response_route, methods=["GET"]),
            Route("/api/text-resp", text_response_route, methods=["GET"]),
            Route("/api/html-resp", html_response_route, methods=["GET"]),
            Route("/api/file-resp", file_response_route, methods=["GET"]),
            Route("/api/check_depend_contextmanager", depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_depend_async_contextmanager", depend_async_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_contextmanager", pre_depend_contextmanager_route, methods=["GET"]),
            Route("/api/check_pre_depend_async_contextmanager", pre_depend_async_contextmanager_route, methods=["GET"]),
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
