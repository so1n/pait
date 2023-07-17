from contextlib import contextmanager
from typing import Iterator

from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from pait.app.starlette import Pait
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.exceptions import ValidationError as _ValidationError
from pait.model import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)


def api_exception(request: Request, exc: Exception) -> Response:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, PaitBaseParamException):
        return JSONResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, PaitBaseException):
        return JSONResponse({"code": -1, "msg": str(exc)})
    elif isinstance(exc, (ValidationError, _ValidationError)):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JSONResponse({"code": -1, "msg": f"miss param: {error_param_list}"})
    elif isinstance(exc, HTTPException):
        return HTMLResponse(status_code=exc.status_code, content=str(exc), headers=getattr(exc, "headers", {}))
    return JSONResponse({"code": -1, "msg": str(exc)})


@contextmanager
def create_app() -> Iterator[Starlette]:
    import uvicorn
    from starlette.applications import Starlette

    from pait.extra.config import apply_block_http_method_set
    from pait.g import config
    from pait.openapi.doc_route import add_doc_route

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Starlette = Starlette()
    yield app
    app.add_exception_handler(Exception, api_exception)
    add_doc_route(prefix="/api-doc", title="Api Doc", app=app)
    uvicorn.run(app)
