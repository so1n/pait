import random
import string
from typing import Optional

from werkzeug.exceptions import BadRequest

from example.common import tag
from example.common.response_model import NotAuthenticated403RespModel, SuccessRespModel, link_login_token_model
from example.common.security import User, get_current_user, temp_token_dict
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.app.flask.security import api_key, http, oauth2
from pait.field import Cookie, Depends, Header, Query
from pait.model import Http400RespModel, Http401RespModel, Http403RespModel, PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
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
    response_model_list=[Http400RespModel, oauth2.OAuth2PasswordBearerJsonRespModel],
)
def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> dict:
    if form_data.username != form_data.password:
        raise BadRequest()
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
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
http_pait = security_pait.create_sub_pait(
    status=PaitStatus.test,
    append_tag=(tag.http_tag,),
)


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


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/api-cookie-key", view_func=api_key_cookie_route, methods=["GET"])
        app.add_url_rule("/api/api-header-key", view_func=api_key_header_route, methods=["GET"])
        app.add_url_rule("/api/api-query-key", view_func=api_key_query_route, methods=["GET"])
        app.add_url_rule("/api/oauth2-login", view_func=oauth2_login, methods=["POST"])
        app.add_url_rule("/api/oauth2-user-name", view_func=oauth2_user_name, methods=["GET"])
        app.add_url_rule("/api/oauth2-user-info", view_func=oauth2_user_info, methods=["GET"])
        app.add_url_rule(
            "/api/user-name-by-http-basic-credentials",
            view_func=get_user_name_by_http_basic_credentials,
            methods=["GET"],
        )
        app.add_url_rule("/api/user-name-by-http-bearer", view_func=get_user_name_by_http_bearer, methods=["GET"])
        app.add_url_rule("/api/user-name-by-http-digest", view_func=get_user_name_by_http_digest, methods=["GET"])
