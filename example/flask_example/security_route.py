from example.common import tag
from example.common.response_model import NotAuthenticatedRespModel, SuccessRespModel, link_login_token_model
from example.flask_example.utils import api_exception, global_pait
from pait.app.flask import Pait
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
    response_model_list=[SuccessRespModel, NotAuthenticatedRespModel],
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


if __name__ == "__main__":
    from flask import Flask

    from pait.app.flask import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Flask = Flask(__name__)
    app.add_url_rule("/api/security/api-key", view_func=api_key_route, methods=["GET"])
    app.errorhandler(Exception)(api_exception)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.run(port=8000, debug=True)
