from pydantic import ValidationError
from tornado.web import HTTPError, RequestHandler

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
