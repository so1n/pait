from contextlib import contextmanager
from typing import Any, Dict, Iterator, Union

from flask import Flask, Response, make_response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from pait.app.flask import Pait
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.model.status import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)


def api_exception(exc: Exception) -> Union[Dict[str, Any], Response]:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return {"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"}
    elif isinstance(exc, PaitBaseException):
        return {"code": -1, "msg": str(exc)}
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return {"code": -1, "msg": f"miss param: {error_param_list}"}
    elif isinstance(exc, HTTPException):
        resp: Response = make_response(str(exc), exc.code)
        resp.headers.update(getattr(exc, "headers", {}) or {})
        return resp
    return {"code": -1, "msg": str(exc)}


@contextmanager
def create_app(name: str) -> Iterator[Flask]:

    from pait.app.flask import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Flask = Flask(name)
    yield app
    app.errorhandler(Exception)(api_exception)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    app.run(port=8000, debug=True)
