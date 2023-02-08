import random
import string

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from example.common import tag
from example.common.response_model import NotAuthenticated403TextRespModel, SuccessRespModel, link_login_token_model
from example.starlette_example.utils import create_app, global_pait
from pait.app.starlette import Pait
from pait.app.starlette.security import api_key, oauth2
from pait.field import Depends, Header
from pait.model.response import Http400RespModel, Http401RespModel, TextResponseModel
from pait.model.status import PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
)


@security_pait(
    status=PaitStatus.test,
    append_tag=(tag.links_tag,),
    response_model_list=[SuccessRespModel, NotAuthenticated403TextRespModel],
)
def api_key_route(
    token: str = Depends.i(
        api_key.APIKey(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        )
    )
) -> JSONResponse:
    return JSONResponse({"token": token})


_temp_token_dict: dict = {}


@security_pait(
    status=PaitStatus.test,
    response_model_list=[
        oauth2.OAuth2PasswordBearerJsonRespModel,
        Http400RespModel.clone(resp_model=TextResponseModel),
    ],
)
async def oauth2_login(form_data: oauth2.OAuth2PasswordRequestFrom) -> JSONResponse:
    if form_data.username != form_data.password:
        raise HTTPException(400)
    token: str = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    _temp_token_dict[token] = form_data.username
    return JSONResponse(oauth2.OAuth2PasswordBearerJsonRespModel.response_data(access_token=token).dict())


@security_pait(
    status=PaitStatus.test,
    response_model_list=[
        SuccessRespModel,
        Http400RespModel.clone(resp_model=TextResponseModel),
        Http401RespModel.clone(resp_model=TextResponseModel),
    ],
)
def oauth2_user_name(token: str = Depends.i(oauth2.OAuth2PasswordBearer(route=oauth2_login))) -> JSONResponse:
    if token not in _temp_token_dict:
        raise HTTPException(400)
    return JSONResponse({"code": 0, "msg": "", "data": _temp_token_dict[token]})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route("/api/security/api-key", api_key_route, methods=["GET"])
        app.add_route("/api/security/oauth2-login", oauth2_login, methods=["POST"])
        app.add_route("/api/security/oauth2-user-name", oauth2_user_name, methods=["GET"])
