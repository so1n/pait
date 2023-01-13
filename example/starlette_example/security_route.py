from starlette.responses import JSONResponse

from example.common import tag
from example.common.response_model import NotAuthenticatedTextRespModel, SuccessRespModel, link_login_token_model
from example.starlette_example.utils import create_app, global_pait
from pait.app.starlette import Pait
from pait.app.starlette.security.api_key import api_key
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
    response_model_list=[SuccessRespModel, NotAuthenticatedTextRespModel],
)
def api_key_route(
    token: str = Depends.i(
        api_key(
            name="token",
            field=Header(links=link_login_token_model, openapi_include=False),
            verify_api_key_callable=lambda x: x == "my-token",
        )
    )
) -> JSONResponse:
    return JSONResponse({"token": token})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route("/api/security/api-key", api_key_route, methods=["GET"])
