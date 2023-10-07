from typing import Optional

from flask import Flask

from pait.app.flask import pait
from pait.app.flask.security import http
from pait.field import Depends
from pait.openapi.doc_route import AddDocRoute

##############
# HTTP Basic #
##############
http_basic: http.HTTPBasic = http.HTTPBasic()


def get_user_name(credentials: Optional[http.HTTPBasicCredentials] = Depends.i(http_basic)) -> str:
    if not credentials or credentials.username != credentials.password:
        raise http_basic.not_authorization_exc
    return credentials.username


@pait()
def get_user_name_by_http_basic_credentials(user_name: str = Depends.t(get_user_name)) -> dict:
    return {"code": 0, "msg": "", "data": user_name}


#############
# HTTP Bear #
#############
http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)


@pait()
def get_user_name_by_http_bearer(credentials: Optional[str] = Depends.i(http_bear)) -> dict:
    return {"code": 0, "msg": "", "data": credentials}


###############
# HTTP Digest #
###############
http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)


@pait()
def get_user_name_by_http_digest(credentials: Optional[str] = Depends.i(http_digest)) -> dict:
    return {"code": 0, "msg": "", "data": credentials}


app = Flask("demo")
app.add_url_rule(
    "/api/user-name-by-http-basic-credentials",
    view_func=get_user_name_by_http_basic_credentials,
    methods=["GET"],
)
app.add_url_rule("/api/user-name-by-http-bearer", view_func=get_user_name_by_http_bearer, methods=["GET"])
app.add_url_rule("/api/user-name-by-http-digest", view_func=get_user_name_by_http_digest, methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
