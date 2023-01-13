from typing import Any, Dict, List, Optional

from starlette.responses import JSONResponse

from example.common import tag
from example.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.common.response_model import FailRespModel, SimpleRespModel, UserSuccessRespModel
from example.starlette_example.utils import api_exception, global_pait
from pait.app.starlette import Pait
from pait.field import Cookie, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.model.status import PaitStatus

field_pait: Pait = global_pait.create_sub_pait(
    group="field",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


@field_pait(
    append_tag=(tag.user_tag, tag.post_tag),
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


@field_pait(
    tag=(tag.same_alias_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}})


@field_pait(
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


@field_pait(
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


@field_pait(status=PaitStatus.test, response_model_list=[SimpleRespModel, FailRespModel])
async def pait_model_route(test_pait_model: TestPaitModel) -> JSONResponse:
    """Test pait model"""
    return JSONResponse({"code": 0, "msg": "", "data": test_pait_model.dict()})


if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route

    from pait.app.starlette import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Starlette = Starlette(
        routes=[
            Route("/api/post", post_route, methods=["POST"]),
            Route("/api/pait-base-field/{age}", pait_base_field_route, methods=["POST"]),
            Route("/api/field-default-factory", field_default_factory_route, methods=["POST"]),
            Route("/api/same-alias", same_alias_route, methods=["GET"]),
            Route("/api/pait-model", pait_model_route, methods=["POST"]),
        ]
    )
    app.add_exception_handler(Exception, api_exception)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    uvicorn.run(app)