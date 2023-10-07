from flask import Flask

from pait.app.flask import pait
from pait.app.flask.security import api_key
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
def api_key_cookie_route(token: str = Depends.i(token_cookie_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


@pait()
def api_key_header_route(token: str = Depends.i(token_header_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


@pait()
def api_key_query_route(token: str = Depends.i(token_query_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


app = Flask("demo")
app.add_url_rule("/api/api-cookie-key", view_func=api_key_cookie_route, methods=["GET"])
app.add_url_rule("/api/api-header-key", view_func=api_key_header_route, methods=["GET"])
app.add_url_rule("/api/api-query-key", view_func=api_key_query_route, methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
