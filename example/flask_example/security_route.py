import random
import string

from werkzeug.exceptions import BadRequest

from example.common import tag
from example.common.response_model import (
    BadRequestRespModel,
    NotAuthenticated401RespModel,
    NotAuthenticated403RespModel,
    SuccessRespModel,
    link_login_token_model,
)
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.app.flask.security import oauth2
from pait.app.flask.security.api_key import api_key
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
def api_key_route(
    token: str = Depends.i(
        api_key(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        ),
    )
) -> dict:
    return {"token": token}


_temp_token_dict: dict = {}


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
)
def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> dict:
    if form_data.username != form_data.password:
        raise BadRequest()
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    _temp_token_dict[token] = form_data.username
    return {"access_token": token, "token_type": "bearer"}


@security_pait(
    status=PaitStatus.test,
    response_model_list=[SuccessRespModel, NotAuthenticated401RespModel, BadRequestRespModel],
)
def oauth2_user_name(token: str = Depends.i(oauth2.oauth_2_password_bearer(route=oauth2_login))) -> dict:
    if token not in _temp_token_dict:
        raise BadRequest()

    return {"code": 0, "msg": "", "data": _temp_token_dict[token]}


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/security/api-key", view_func=api_key_route, methods=["GET"])
        app.add_url_rule("/api/security/oauth2-login", view_func=oauth2_login, methods=["POST"])
        app.add_url_rule("/api/security/oauth2-user-name", view_func=oauth2_user_name, methods=["GET"])
