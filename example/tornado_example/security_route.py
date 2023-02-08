import random
import string

from tornado.web import HTTPError

from example.common import tag
from example.common.response_model import (
    BadRequestRespModel,
    NotAuthenticated401RespModel,
    NotAuthenticated403RespModel,
    SuccessRespModel,
    link_login_token_model,
)
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.app.tornado.security import api_key, oauth2
from pait.field import Depends, Header
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


_temp_token_dict: dict = {}


class OAuth2LoginHandler(MyHandler):
    @security_pait(
        status=PaitStatus.test,
        response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
    )
    async def post(self, form_data: oauth2.OAuth2PasswordRequestFrom) -> None:
        if form_data.username != form_data.password:
            raise HTTPError(400)
        token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        _temp_token_dict[token] = form_data.username
        self.write({"access_token": token, "token_type": "bearer"})


class OAuth2UserNameHandler(MyHandler):
    @security_pait(
        status=PaitStatus.test,
        response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
    )
    def get(self, token: str = Depends.i(oauth2.OAuth2PasswordBearer(route=OAuth2LoginHandler.post))) -> None:
        if token not in _temp_token_dict:
            raise HTTPError(400)
        self.write({"code": 0, "msg": "", "data": _temp_token_dict[token]})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/security/api-key", APIKeyHanler),
                (r"/api/security/oauth2-login", OAuth2LoginHandler),
                (r"/api/security/oauth2-user-name", OAuth2UserNameHandler),
            ]
        )
