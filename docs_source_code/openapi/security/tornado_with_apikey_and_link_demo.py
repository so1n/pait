import hashlib
from typing import Type

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.security import api_key
from pait.field import Depends, Json, Query
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute
from pait.openapi.openapi import LinksModel


class LoginRespModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        class DataModel(BaseModel):
            token: str

        code: int = Field(0, description="api code")
        msg: str = Field("success", description="api status msg")
        data: DataModel

    description: str = "login response"
    response_data: Type[BaseModel] = ResponseModel


class LoginHandler(RequestHandler):
    @pait(response_model_list=[LoginRespModel])
    async def post(
        self, uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
    ) -> None:
        self.write(
            {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
        )


link_login_token_model: LinksModel = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


token_query_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Query(links=link_login_token_model),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-query-api-key",
)


class APIKeyQueryHandler(RequestHandler):
    @pait()
    async def get(self, token: str = Depends.i(token_query_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


app: Application = Application(
    [
        (r"/api/login", LoginHandler),
        (r"/api/security/api-query-key", APIKeyQueryHandler),
    ],
)
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
