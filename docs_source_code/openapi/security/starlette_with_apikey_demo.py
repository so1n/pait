from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.app.starlette.security import api_key
from pait.field import Cookie, Depends, Header, Query
from pait.openapi.doc_route import AddDocRoute

token_cookie_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Cookie(openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-cookie-api-key",
)
token_header_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Header(openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-header-api-key",
)
token_query_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Query(openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-query-api-key",
)


@pait()
async def api_key_cookie_route(token: str = Depends.i(token_cookie_api_key)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": token})


@pait()
async def api_key_header_route(token: str = Depends.i(token_header_api_key)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": token})


@pait()
async def api_key_query_route(token: str = Depends.i(token_query_api_key)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": token})


app = Starlette(
    routes=[
        Route("/api/api-cookie-key", api_key_cookie_route, methods=["GET"]),
        Route("/api/api-header-key", api_key_header_route, methods=["GET"]),
        Route("/api/api-query-key", api_key_query_route, methods=["GET"]),
    ]
)
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
