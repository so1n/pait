from typing import Optional

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.security import http
from pait.field import Depends
from pait.openapi.doc_route import AddDocRoute

http_basic: http.HTTPBasic = http.HTTPBasic()


def get_user_name(credentials: Optional[http.HTTPBasicCredentials] = Depends.t(http_basic)) -> str:
    if not credentials or credentials.username != credentials.password:
        raise http_basic.not_authorization_exc
    return credentials.username


class UserNameByHttpBasicCredentialsHandler(RequestHandler):
    @pait()
    async def get(self, user_name: str = Depends.t(get_user_name)) -> None:
        self.write({"code": 0, "msg": "", "data": user_name})


#############
# HTTP Bear #
#############
http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)


class UserNameByHttpBearerHandler(RequestHandler):
    @pait()
    async def get(self, credentials: Optional[str] = Depends.t(http_bear)) -> None:
        self.write({"code": 0, "msg": "", "data": credentials})


###############
# HTTP Digest #
###############
http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)


class UserNameByHttpDigestHandler(RequestHandler):
    @pait()
    async def get(self, credentials: Optional[str] = Depends.t(http_digest)) -> None:
        self.write({"code": 0, "msg": "", "data": credentials})


app: Application = Application(
    [
        (r"/api/security/user-name-by-http-basic-credentials", UserNameByHttpBasicCredentialsHandler),
        (r"/api/security/user-name-by-http-bearer", UserNameByHttpBearerHandler),
        (r"/api/security/user-name-by-http-digest", UserNameByHttpDigestHandler),
    ],
)
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
