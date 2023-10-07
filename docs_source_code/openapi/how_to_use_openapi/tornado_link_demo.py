import hashlib
from typing import Type

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait
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


class LoginHandler(RequestHandler):
    @pait(response_model_list=[LoginRespModel])
    async def post(
        self, uid: str = field.Json.i(description="user id"), password: str = field.Json.i(description="password")
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
        )


class GetUserHandler(RequestHandler):
    @pait()
    def get(
        self,
        token: str = field.Header.i(
            "",
            description="token",
            links=link_login_token_model,
        ),
    ) -> None:
        if token:
            self.write({"code": 0, "msg": ""})
        else:
            self.write({"code": 1, "msg": ""})


app: Application = Application(
    [(r"/api/login", LoginHandler), (r"/api/get-user-info", GetUserHandler)],
)
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
