import hashlib
from typing import Type

from pydantic import BaseModel, Field
from sanic.app import Sanic
from sanic.response import HTTPResponse, json

from pait import field
from pait.app.sanic import pait
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
    uid: str = field.Json.i(description="user id"), password: str = field.Json.i(description="password")
) -> HTTPResponse:
    return json({"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}})


@pait()
def get_user_route(
    token: str = field.Header.i(
        "",
        description="token",
        links=link_login_token_model,
    )
) -> HTTPResponse:
    if token:
        return json({"code": 0, "msg": ""})
    else:
        return json({"code": 1, "msg": ""})


app = Sanic(name="demo")
app.add_route(login_route, "/api/login", methods=["POST"])
app.add_route(get_user_route, "/api/get-user-info", methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
