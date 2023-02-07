import random
import string

from sanic import response
from sanic.exceptions import InvalidUsage

from example.common import tag
from example.common.response_model import (
    BadRequestRespModel,
    NotAuthenticated401RespModel,
    NotAuthenticated403RespModel,
    SuccessRespModel,
    link_login_token_model,
)
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
from pait.app.sanic.security import oauth2
from pait.app.sanic.security.api_key import api_key
from pait.field import Depends, Header
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
        api_key(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        )
    )
) -> response.HTTPResponse:
    return response.json({"token": token})


_temp_token_dict: dict = {}


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
)
async def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> response.HTTPResponse:
    if form_data.username != form_data.password:
        raise InvalidUsage("Bad Request")
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    _temp_token_dict[token] = form_data.username
    return response.json({"access_token": token, "token_type": "bearer"})


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
)
def oauth2_user_name(
    token: str = Depends.i(oauth2.oauth_2_password_bearer(route=oauth2_login)),
) -> response.HTTPResponse:
    if token not in _temp_token_dict:
        raise InvalidUsage("Bad Request")
    return response.json({"code": 0, "msg": "", "data": _temp_token_dict[token]})


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_route(api_key_route, "/api/security/api-key", methods={"GET"})
        app.add_route(oauth2_login, "/api/security/oauth2-login", methods={"POST"})
        app.add_route(oauth2_user_name, "/api/security/oauth2-user-name", methods={"GET"})
