import random
import string

from tornado.web import HTTPError

from example.common import tag
from example.common.response_model import NotAuthenticated403RespModel, SuccessRespModel, link_login_token_model
from example.common.security import User, get_current_user, temp_token_dict
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.app.tornado.security import api_key, oauth2
from pait.field import Cookie, Depends, Header, Query
from pait.model.response import Http400RespModel, Http401RespModel
from pait.model.status import PaitStatus

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
    append_tag=(tag.links_tag,),
    response_model_list=[SuccessRespModel, NotAuthenticated403RespModel],
)


class APIKeyCookieHanler(MyHandler):
    @api_key_pait()
    async def get(self, token: str = Depends.i(token_cookie_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


class APIKeyHeaderHanler(MyHandler):
    @api_key_pait()
    async def get(self, token: str = Depends.i(token_header_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


class APIKeyQueryHanler(MyHandler):
    @api_key_pait()
    async def get(self, token: str = Depends.i(token_query_api_key)) -> None:
        self.write({"code": 0, "msg": "", "data": token})


oauth2_pb: oauth2.OAuth2PasswordBearer = oauth2.OAuth2PasswordBearer(
    scopes={
        "user": "get all user info",
        "user-name": "only get user name",
    }
)


class OAuth2LoginHandler(MyHandler):
    @security_pait(
        status=PaitStatus.test,
        response_model_list=[oauth2.OAuth2PasswordBearerJsonRespModel, Http400RespModel],
    )
    async def post(self, form_data: oauth2.OAuth2PasswordRequestFrom) -> None:
        if form_data.username != form_data.password:
            raise HTTPError(400)
        token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        temp_token_dict[token] = User(uid="123", name=form_data.username, age=23, sex="M", scopes=form_data.scope)
        self.write(oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict())


class OAuth2UserNameHandler(MyHandler):
    @security_pait(
        status=PaitStatus.test,
        response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
    )
    def get(self, user_model: User = Depends.t(get_current_user(["user-name"], oauth2_pb))) -> None:
        self.write({"code": 0, "msg": "", "data": user_model.name})


class OAuth2UserInfoHandler(MyHandler):
    @security_pait(
        status=PaitStatus.test,
        response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
    )
    def get(self, user_model: User = Depends.t(get_current_user(["user"], oauth2_pb))) -> None:
        self.write({"code": 0, "msg": "", "data": user_model.dict()})


oauth2_pb.with_route(OAuth2LoginHandler.post)
if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/security/api-key-cookie-route", APIKeyCookieHanler),
                (r"/api/security/api-key-header-route", APIKeyHeaderHanler),
                (r"/api/security/api-key-query-route", APIKeyQueryHanler),
                (r"/api/security/oauth2-login", OAuth2LoginHandler),
                (r"/api/security/oauth2-user-name", OAuth2UserNameHandler),
                (r"/api/security/oauth2-user-info", OAuth2UserInfoHandler),
            ]
        )
