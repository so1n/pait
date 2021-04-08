from typing import Any, Tuple
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

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
from pait.app.starlette import pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Cookie, Depends, File, Form, Header, Path, Query
from pait.model import PaitStatus


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"exc": str(exc)})


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
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": return_dict
        }
    )


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
    content_type: str = Header.i(alias="Content-Type", description="content-type"),
) -> JSONResponse:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": return_dict
        }
    )


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
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": return_dict
        }
    )


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
) -> JSONResponse:
    """Test Field"""
    return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": age, "sex": sex.value}
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": return_dict
        }
    )


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
)
async def test_other_field(
    upload_file: Any = File.i(description="upload file"),
    a: Any = Form.i(description="form data"),
    b: Any = Form.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie")
) -> JSONResponse:
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "filename": upload_file.filename,
                "content": (await upload_file.read()).decode(),
                "form_a": (await a.read()).decode(),
                "form_b": (await b.read()).decode(),
                "cookie": cookie
            }
        }
    )


@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[UserSuccessRespModel, FailRespModel]
)
async def test_pait_model(test_model: TestPaitModel) -> JSONResponse:
    """Test Field"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": test_model.dict()
        }
    )


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
        return JSONResponse(
            {
                "code": 0,
                "msg": "",
                "data": return_dict
            }
        )

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
        return JSONResponse(
            {
                "code": 0,
                "msg": "",
                "data": return_dict
            }
        )


app = Starlette(
    routes=[
        Route("/api/get/{age}", test_get, methods=["GET"]),
        Route("/api/post", test_post, methods=["POST"]),
        Route("/api/depend", test_depend, methods=["POST"]),
        Route("/api/other_field", test_other_field, methods=["POST"]),
        Route("/api/raise_tip", test_raise_tip, methods=["POST"]),
        Route("/api/cbv", TestCbv),
        Route("/api/pait_model", test_pait_model, methods=["POST"]),
    ]
)

app.add_exception_handler(PaitBaseException, api_exception)
app.add_exception_handler(ValidationError, api_exception)


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(app, log_level="debug")
