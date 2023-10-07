import random
import string
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from pydantic import BaseModel, Field
from tornado.ioloop import IOLoop
from tornado.web import Application, HTTPError, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.security import oauth2
from pait.field import Depends
from pait.model.response import Http400RespModel
from pait.openapi.doc_route import AddDocRoute

if TYPE_CHECKING:
    from pait.app.base.security.oauth2 import BaseOAuth2PasswordBearerProxy


class User(BaseModel):
    uid: str = Field(..., description="user id")
    name: str = Field(..., description="user name")
    age: int = Field(..., description="user age")
    sex: str = Field(..., description="user sex")
    scopes: List[str] = Field(..., description="user scopes")


temp_token_dict: Dict[str, User] = {}


class OAuth2LoginHandler(RequestHandler):
    @pait(
        response_model_list=[oauth2.OAuth2PasswordBearerJsonRespModel, Http400RespModel],
    )
    async def post(self, form_data: oauth2.OAuth2PasswordRequestFrom) -> None:
        if form_data.username != form_data.password:
            raise HTTPError(400)
        token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        temp_token_dict[token] = User(uid="123", name=form_data.username, age=23, sex="M", scopes=form_data.scope)
        self.write(oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict())


oauth2_pb: oauth2.OAuth2PasswordBearer = oauth2.OAuth2PasswordBearer(
    route=OAuth2LoginHandler.post,
    scopes={
        "user-info": "get all user info",
        "user-name": "only get user name",
    },
)


def get_current_user(_oauth2_pb: "BaseOAuth2PasswordBearerProxy") -> Callable[[str], User]:
    def _check_scope(token: str = Depends.i(_oauth2_pb)) -> User:
        user_model: Optional[User] = temp_token_dict.get(token, None)
        if not user_model:
            raise _oauth2_pb.security.not_authenticated_exc
        if not _oauth2_pb.is_allow(user_model.scopes):
            raise _oauth2_pb.security.not_authenticated_exc
        return user_model

    return _check_scope


class OAuth2UserNameHandler(RequestHandler):
    @pait()
    def get(self, user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-name"])))) -> None:
        self.write({"code": 0, "msg": "", "data": user_model.name})


class OAuth2UserInfoHandler(RequestHandler):
    @pait()
    def get(self, user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-info"])))) -> None:
        self.write({"code": 0, "msg": "", "data": user_model.dict()})


app: Application = Application(
    [
        (r"/api/security/oauth2-login", OAuth2LoginHandler),
        (r"/api/security/oauth2-user-name", OAuth2UserNameHandler),
        (r"/api/security/oauth2-user-info", OAuth2UserInfoHandler),
    ],
)
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
