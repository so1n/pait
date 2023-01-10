from example.common import tag
from example.common.response_model import NotAuthenticatedRespModel, SuccessRespModel, link_login_token_model
from example.tornado_example.utils import MyHandler, global_pait
from pait.app.tornado import Pait
from pait.app.tornado.security.api_key import api_key
from pait.field import Depends, Header
from pait.model.status import PaitStatus

security_pait: Pait = global_pait.create_sub_pait(
    group="security",
    status=PaitStatus.release,
    tag=(tag.depend_tag, tag.security_tag),
)


class APIKeyHanler(MyHandler):
    @security_pait(response_model_list=[SuccessRespModel, NotAuthenticatedRespModel])
    async def get(
        self,
        token: str = Depends.i(
            api_key(
                name="token",
                field=Header(links=link_login_token_model, openapi_include=False),
                verify_api_key_callable=lambda x: x == "my-token",
            )
        ),
    ) -> None:
        self.write({"token": token})


if __name__ == "__main__":
    from tornado.ioloop import IOLoop
    from tornado.web import Application

    from pait.app.tornado import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Application = Application(
        [
            (r"/api/security/api-key", APIKeyHanler),
        ]
    )
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.listen(8000)
    IOLoop.instance().start()
