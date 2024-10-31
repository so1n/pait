from typing import Optional

from sanic import Sanic, response

from pait.app.sanic import pait
from pait.app.sanic.security import http
from pait.field import Depends
from pait.openapi.doc_route import AddDocRoute

##############
# HTTP Basic #
##############
http_basic: http.HTTPBasic = http.HTTPBasic()


def get_user_name(credentials: Optional[http.HTTPBasicCredentials] = Depends.t(http_basic)) -> str:
    if not credentials or credentials.username != credentials.password:
        raise http_basic.not_authorization_exc
    return credentials.username


@pait()
async def get_user_name_by_http_basic_credentials(user_name: str = Depends.t(get_user_name)) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": user_name})


#############
# HTTP Bear #
#############
http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)


@pait()
async def get_user_name_by_http_bearer(credentials: Optional[str] = Depends.t(http_bear)) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": credentials})


###############
# HTTP Digest #
###############
http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)


@pait()
async def get_user_name_by_http_digest(credentials: Optional[str] = Depends.t(http_digest)) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": credentials})


app = Sanic(name="demo", configure_logging=False)
app.add_route(get_user_name_by_http_basic_credentials, "/api/user-name-by-http-basic-credentials", methods={"GET"})
app.add_route(get_user_name_by_http_bearer, "/api/user-name-by-http-bearer", methods={"GET"})
app.add_route(get_user_name_by_http_digest, "/api/user-name-by-http-digest", methods={"GET"})
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
