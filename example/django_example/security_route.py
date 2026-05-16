import os
import random
import string
import sys
from typing import Optional

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.core.exceptions import BadRequest

from example.common import tag
from example.common.response_model import NotAuthenticated403RespModel, SuccessRespModel, link_login_token_model
from example.common.security import User, get_current_user, temp_token_dict
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.app.django.plugin import UnifiedResponsePlugin
from pait.app.django.security import api_key, http, oauth2
from pait.field import Cookie, Depends, Header, Query
from pait.model.response import Http400RespModel, Http401RespModel, Http403RespModel
from pait.model.status import PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
    plugin_list=[UnifiedResponsePlugin.build()],
)

token_cookie_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Cookie(links=link_login_token_model, openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-cookie-api-key",
)
token_header_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Header(links=link_login_token_model, openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-header-api-key",
)
token_query_api_key: api_key.APIKey = api_key.APIKey(
    name="token",
    field=Query(links=link_login_token_model, openapi_include=False),
    verify_api_key_callable=lambda x: "token" in x,
    security_name="token-query-api-key",
)

api_key_pait = security_pait.create_sub_pait(
    status=PaitStatus.test,
    append_tag=(tag.api_key_tag,),
    response_model_list=[SuccessRespModel, NotAuthenticated403RespModel],
)


@api_key_pait()
def api_key_cookie_route(token: str = Depends.t(token_cookie_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


@api_key_pait()
def api_key_header_route(token: str = Depends.t(token_header_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


@api_key_pait()
def api_key_query_route(token: str = Depends.t(token_query_api_key)) -> dict:
    return {"code": 0, "msg": "", "data": token}


oauth2_pb: oauth2.OAuth2PasswordBearer = oauth2.OAuth2PasswordBearer(
    scopes={
        "user-info": "get all user info",
        "user-name": "only get user name",
    }
)


@security_pait(
    status=PaitStatus.test,
    append_tag=(tag.oauth2_tag,),
    response_model_list=[oauth2.OAuth2PasswordBearerJsonRespModel, Http400RespModel],
)
def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> dict:
    if form_data.username != form_data.password:
        raise BadRequest()
    token = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    temp_token_dict[token] = User(uid="123", name=form_data.username, age=23, sex="M", scopes=form_data.scope)
    return oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict()


oauth2_pb.with_route(oauth2_login)


@security_pait(
    status=PaitStatus.test,
    append_tag=(tag.oauth2_tag,),
    response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
)
def oauth2_user_name(user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-name"])))) -> dict:
    return {"code": 0, "msg": "", "data": user_model.name}


@security_pait(
    status=PaitStatus.test,
    append_tag=(tag.oauth2_tag,),
    response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
)
def oauth2_user_info(user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-info"])))) -> dict:
    return {"code": 0, "msg": "", "data": user_model.dict()}


http_basic: http.HTTPBasic = http.HTTPBasic()
http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)
http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)
http_pait = security_pait.create_sub_pait(status=PaitStatus.test, append_tag=(tag.http_tag,))


def get_user_name(credentials: Optional[http.HTTPBasicCredentials] = Depends.i(http_basic)) -> str:
    if not credentials or credentials.username != credentials.password:
        raise http_basic.not_authorization_exc
    return credentials.username


@http_pait(response_model_list=[SuccessRespModel, Http401RespModel])
def get_user_name_by_http_basic_credentials(user_name: str = Depends.t(get_user_name)) -> dict:
    return {"code": 0, "msg": "", "data": user_name}


@http_pait(response_model_list=[SuccessRespModel, Http403RespModel])
def get_user_name_by_http_bearer(credentials: Optional[str] = Depends.i(http_bear)) -> dict:
    return {"code": 0, "msg": "", "data": credentials}


@http_pait(response_model_list=[SuccessRespModel, Http403RespModel])
def get_user_name_by_http_digest(credentials: Optional[str] = Depends.i(http_digest)) -> dict:
    return {"code": 0, "msg": "", "data": credentials}


urlpatterns = [
    route_path("api/security/api-cookie-key", api_key_cookie_route, ["GET"], name="security_api_cookie_key"),
    route_path("api/security/api-header-key", api_key_header_route, ["GET"], name="security_api_header_key"),
    route_path("api/security/api-query-key", api_key_query_route, ["GET"], name="security_api_query_key"),
    route_path("api/security/oauth2-login", oauth2_login, ["POST"], name="security_oauth2_login"),
    route_path("api/security/oauth2-user-name", oauth2_user_name, ["GET"], name="security_oauth2_user_name"),
    route_path("api/security/oauth2-user-info", oauth2_user_info, ["GET"], name="security_oauth2_user_info"),
    route_path(
        "api/security/user-name-by-http-basic-credentials",
        get_user_name_by_http_basic_credentials,
        ["GET"],
        name="security_http_basic",
    ),
    route_path(
        "api/security/user-name-by-http-bearer",
        get_user_name_by_http_bearer,
        ["GET"],
        name="security_http_bearer",
    ),
    route_path(
        "api/security/user-name-by-http-digest",
        get_user_name_by_http_digest,
        ["GET"],
        name="security_http_digest",
    ),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.security_route_urlconf")
