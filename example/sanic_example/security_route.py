import random
import string

from sanic import response
from sanic.exceptions import InvalidUsage

from example.common import tag
from example.common.response_model import NotAuthenticated403RespModel, SuccessRespModel, link_login_token_model
from example.common.security import User, get_current_user, temp_token_dict
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
from pait.app.sanic.security import api_key, oauth2
from pait.field import Depends, Header
from pait.model.response import Http400RespModel, Http401RespModel
from pait.model.status import PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
)


@security_pait(
    status=PaitStatus.test,
    append_tag=(tag.links_tag,),
    response_model_list=[SuccessRespModel, NotAuthenticated403RespModel],
)
async def api_key_route(
    token: str = Depends.i(
        api_key.APIKey(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        )
    )
) -> response.HTTPResponse:
    return response.json({"token": token})


oauth2_pb: oauth2.OAuth2PasswordBearer = oauth2.OAuth2PasswordBearer(
    scopes={
        "user": "get all user info",
        "user-name": "only get user name",
    }
)


@security_pait(
    status=PaitStatus.test,
    response_model_list=[Http400RespModel, oauth2.OAuth2PasswordBearerJsonRespModel],
)
async def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> response.HTTPResponse:
    if form_data.username != form_data.password:
        raise InvalidUsage("Bad Request")
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    temp_token_dict[token] = User(uid="123", name=form_data.username, age=23, sex="M", scopes=form_data.scope)
    return response.json(oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict())


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
)
def oauth2_user_name(
    user_model: User = Depends.t(get_current_user(["user-name"], oauth2_pb)),
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": user_model.name})


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, Http400RespModel, Http401RespModel],
)
def oauth2_user_info(
    user_model: User = Depends.t(get_current_user(["user"], oauth2_pb)),
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": user_model.dict()})


oauth2_pb.with_route(oauth2_login)
if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_route(api_key_route, "/api/security/api-key", methods={"GET"})
        app.add_route(oauth2_login, "/api/security/oauth2-login", methods={"POST"})
        app.add_route(oauth2_user_name, "/api/security/oauth2-user-name", methods={"GET"})
        app.add_route(oauth2_user_info, "/api/security/oauth2-user-info", methods={"GET"})
