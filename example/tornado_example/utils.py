from contextlib import contextmanager
from typing import Iterator

from pydantic import ValidationError
from tornado.routing import _RuleList
from tornado.web import AnyMatches, Application, HTTPError, RequestHandler, Rule, _ApplicationRouter

from pait.app.tornado import Pait
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.model.status import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)


class MyHandler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, PaitBaseParamException):
            self.write({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
        elif isinstance(exc, PaitBaseException):
            self.write({"code": -1, "msg": str(exc)})
        elif isinstance(exc, ValidationError):
            error_param_list: list = []
            for i in exc.errors():
                error_param_list.extend(i["loc"])
            self.write({"code": -1, "msg": f"miss param: {error_param_list}"})
        elif isinstance(exc, HTTPError):
            self.set_status(exc.status_code, exc.reason)
            self.write_error(exc.status_code)
            return
        else:
            self.write({"code": -1, "msg": str(exc)})
        self.finish()


class MyApplication(Application):
    def add_route(self, rules: _RuleList) -> None:
        self.wildcard_router.add_rules(rules)
        self.default_router = _ApplicationRouter(self, [Rule(AnyMatches(), self.wildcard_router)])


@contextmanager
def create_app() -> Iterator[MyApplication]:
    import logging

    from tornado.ioloop import IOLoop

    from pait.app.tornado import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    logging.basicConfig(
        format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.DEBUG
    )

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: MyApplication = MyApplication()
    yield app
    app.listen(8000)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    IOLoop.instance().start()
