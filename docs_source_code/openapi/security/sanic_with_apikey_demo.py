from sanic import HTTPResponse, Sanic, json

from pait.app.sanic import pait
from pait.app.sanic.security import api_key
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
async def api_key_cookie_route(token: str = Depends.i(token_cookie_api_key)) -> HTTPResponse:
    return json({"code": 0, "msg": "", "data": token})


@pait()
async def api_key_header_route(token: str = Depends.i(token_header_api_key)) -> HTTPResponse:
    return json({"code": 0, "msg": "", "data": token})


@pait()
async def api_key_query_route(token: str = Depends.i(token_query_api_key)) -> HTTPResponse:
    return json({"code": 0, "msg": "", "data": token})


app = Sanic(name="demo", configure_logging=False)
app.add_route(api_key_cookie_route, "/api/api-cookie-key", methods=["GET"])
app.add_route(api_key_header_route, "/api/api-header-key", methods=["GET"])
app.add_route(api_key_query_route, "/api/api-query-key", methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
