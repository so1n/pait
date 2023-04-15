from contextlib import contextmanager
from typing import Iterator

from pydantic import ValidationError
from sanic import Request, Sanic, response
from sanic.exceptions import SanicException

from pait.app.sanic import Pait
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.model import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)


async def api_exception(request: Request, exc: Exception) -> response.HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return response.json({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, PaitBaseException):
        return response.json({"code": -1, "msg": str(exc)})
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return response.json({"code": -1, "msg": f"miss param: {error_param_list}"})
    elif isinstance(exc, SanicException):
        return response.html(str(exc), status=exc.status_code, headers=getattr(exc, "headers", {}))
    return response.json({"code": -1, "msg": str(exc)})


@contextmanager
def create_app(name: str) -> Iterator[Sanic]:
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config
    from pait.openapi.doc_route import add_doc_route

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Sanic = Sanic(name)
    yield app
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.run(port=8000, debug=True)
