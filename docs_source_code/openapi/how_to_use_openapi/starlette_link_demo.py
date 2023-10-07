import hashlib
from typing import Type

from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute
from pait.openapi.openapi import LinksModel


class LoginRespModel(JsonResponseModel):
    class ResponseModel(BaseModel):  # type: ignore
        class DataModel(BaseModel):
            token: str

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "login response"
    response_data: Type[BaseModel] = ResponseModel


link_login_token_model: LinksModel = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


@pait(response_model_list=[LoginRespModel])
async def login_route(
    uid: str = field.Body.i(description="user id"), password: str = field.Body.i(description="password")
) -> JSONResponse:
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


@pait()
async def get_user_route(
    token: str = field.Header.i(
        "",
        description="token",
        links=link_login_token_model,
    )
) -> JSONResponse:
    if token:
        return JSONResponse({"code": 0, "msg": ""})
    else:
        return JSONResponse({"code": 1, "msg": ""})


app = Starlette(
    routes=[
        Route("/api/login", login_route, methods=["POST"]),
        Route("/api/get-user-info", get_user_route, methods=["GET"]),
    ]
)
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
