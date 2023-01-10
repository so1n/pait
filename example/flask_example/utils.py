from typing import Any, Dict

from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from pait.app.flask import Pait
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.model.status import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)


def api_exception(exc: Exception) -> Dict[str, Any]:
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
        raise exc
    return {"code": -1, "msg": str(exc)}
