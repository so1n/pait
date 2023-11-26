import hashlib
from typing import Type

from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.app.starlette.security import api_key
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


@pait(response_model_list=[LoginRespModel])
async def login_route(
    uid: str = Json.i(description="user id"), password: str = Json.i(description="password")
) -> JSONResponse:
    return JSONResponse(
        {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}
    )


link_login_token_model: LinksModel = LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model")


token_query_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Query(links=link_login_token_model),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-query-api-key",
)


@pait()
async def api_key_query_route(token: str = Depends.i(token_query_api_key)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": token})


app = Starlette(
    routes=[
        Route("/api/login", login_route, methods=["POST"]),
        Route("/api/api-query-key", api_key_query_route, methods=["GET"]),
    ]
)
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
