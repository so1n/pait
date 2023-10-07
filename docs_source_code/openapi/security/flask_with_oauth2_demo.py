import random
import string
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from flask import Flask
from pydantic import BaseModel, Field
from werkzeug.exceptions import BadRequest

from pait.app.flask import pait
from pait.app.flask.security import oauth2
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


@pait(
    response_model_list=[Http400RespModel, oauth2.OAuth2PasswordBearerJsonRespModel],
)
def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> dict:
    if form_data.username != form_data.password:
        raise BadRequest()
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    temp_token_dict[token] = User(uid="123", name=form_data.username, age=23, sex="M", scopes=form_data.scope)
    return oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict()


oauth2_pb: oauth2.OAuth2PasswordBearer = oauth2.OAuth2PasswordBearer(
    route=oauth2_login,
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


@pait()
def oauth2_user_name(user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-name"])))) -> dict:
    return {"code": 0, "msg": "", "data": user_model.name}


@pait()
def oauth2_user_info(user_model: User = Depends.t(get_current_user(oauth2_pb.get_depend(["user-info"])))) -> dict:
    return {"code": 0, "msg": "", "data": user_model.dict()}


app = Flask("demo")
app.add_url_rule("/api/oauth2-login", view_func=oauth2_login, methods=["POST"])
app.add_url_rule("/api/oauth2-user-name", view_func=oauth2_user_name, methods=["GET"])
app.add_url_rule("/api/oauth2-user-info", view_func=oauth2_user_info, methods=["GET"])
AddDocRoute(app)


if __name__ == "__main__":
    app.run(port=8000)
