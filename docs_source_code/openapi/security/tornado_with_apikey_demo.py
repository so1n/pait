from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.security import api_key
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


class APIKeyCookieHandler(RequestHandler):
    @pait()
    async def get(self, token: str = Depends.i(token_cookie_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


class APIKeyHeaderHandler(RequestHandler):
    @pait()
    async def get(self, token: str = Depends.i(token_header_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


class APIKeyQueryHandler(RequestHandler):
    @pait()
    async def get(self, token: str = Depends.i(token_query_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


app: Application = Application(
    [
        (r"/api/security/api-cookie-key", APIKeyCookieHandler),
        (r"/api/security/api-header-key", APIKeyHeaderHandler),
        (r"/api/security/api-query-key", APIKeyQueryHandler),
    ],
)
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
