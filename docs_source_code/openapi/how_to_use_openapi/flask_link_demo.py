import hashlib
from typing import Type

from flask import Flask
from pydantic import BaseModel, Field

from pait import field
from pait.app.flask import pait
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
def login_route(
    uid: str = field.Body.i(description="user id"), password: str = field.Body.i(description="password")
) -> dict:
    return {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}


@pait()
def get_user_route(token: str = field.Header.i("", description="token", links=link_login_token_model)) -> dict:
    if token:
        return {"code": 0, "msg": ""}
    else:
        return {"code": 1, "msg": ""}


app = Flask("demo")
app.add_url_rule("/api/login", "login", login_route, methods=["POST"])
app.add_url_rule("/api/get-user-info", "get_user_info", get_user_route, methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
