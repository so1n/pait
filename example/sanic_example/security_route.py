from sanic import response

from example.common import tag
from example.common.response_model import NotAuthenticatedRespModel, SuccessRespModel, link_login_token_model
from example.sanic_example.utils import api_exception, global_pait
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
    from sanic import Sanic

    from pait.app.sanic import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Sanic = Sanic(__name__)
    app.add_route(api_key_route, "/api/security/api-key", methods={"GET"})
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.exception(Exception)(api_exception)
    app.run(port=8000, debug=True)
