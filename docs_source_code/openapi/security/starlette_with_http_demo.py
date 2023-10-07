from typing import Optional

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.app.starlette.security import http
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
async def get_user_name_by_http_basic_credentials(user_name: str = Depends.t(get_user_name)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": user_name})


#############
# HTTP Bear #
#############
http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)


@pait()
async def get_user_name_by_http_bearer(credentials: Optional[str] = Depends.t(http_bear)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": credentials})


###############
# HTTP Digest #
###############
http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)


@pait()
async def get_user_name_by_http_digest(credentials: Optional[str] = Depends.t(http_digest)) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": credentials})


app = Starlette(
    routes=[
        Route("/api/user-name-by-http-basic-credentials", get_user_name_by_http_basic_credentials, methods=["GET"]),
        Route("/api/user-name-by-http-bearer", get_user_name_by_http_bearer, methods=["GET"]),
        Route("/api/user-name-by-http-digest", get_user_name_by_http_digest, methods=["GET"]),
    ]
)
AddDocRoute(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
