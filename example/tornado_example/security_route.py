import random
import string

from tornado.web import HTTPError

from example.common import tag
from example.common.response_model import NotAuthenticated403RespModel, SuccessRespModel, link_login_token_model
from example.common.security import User, get_current_user, temp_token_dict
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.app.tornado.security import api_key, oauth2
from pait.field import Depends, Header
from pait.model.response import Http400RespModel, Http401RespModel
from pait.model.status import PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
)


class APIKeyHanler(MyHandler):
    @security_pait(response_model_list=[SuccessRespModel, NotAuthenticated403RespModel])
    async def get(
        self,
        token: str = Depends.i(
            api_key.APIKey(
                name="token",
                field=Header(links=link_login_token_model, openapi_include=False),
                verify_api_key_callable=lambda x: x == "my-token",
            )
        ),
    ) -> None:
        self.write({"token": token})


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
                (r"/api/security/api-key", APIKeyHanler),
                (r"/api/security/oauth2-login", OAuth2LoginHandler),
                (r"/api/security/oauth2-user-name", OAuth2UserNameHandler),
                (r"/api/security/oauth2-user-info", OAuth2UserInfoHandler),
            ]
        )
