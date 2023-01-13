from sanic import response

from example.common import tag
from example.common.response_model import NotAuthenticatedRespModel, SuccessRespModel, link_login_token_model
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
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
    response_model_list=[SuccessRespModel, NotAuthenticatedRespModel],
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


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_route(api_key_route, "/api/security/api-key", methods={"GET"})
