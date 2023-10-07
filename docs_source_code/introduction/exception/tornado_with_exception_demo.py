from typing import List

from pydantic import ValidationError
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import exceptions, field
from pait.app.tornado import pait
from pait.openapi.doc_route import AddDocRoute


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, exceptions.TipException):
            exc = exc.exc

        if isinstance(exc, exceptions.PaitBaseParamException):
            self.write({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
        elif isinstance(exc, ValidationError):
            error_param_list: List = []
            for i in exc.errors():
                error_param_list.extend(i["loc"])
            self.write({"code": -1, "msg": f"check error param: {error_param_list}"})
        elif isinstance(exc, exceptions.PaitBaseException):
            self.write({"code": -1, "msg": str(exc)})

        self.finish()


class DemoHandler(_Handler):
    @pait()
    async def get(self, demo_value: int = field.Query.i()) -> None:
        self.write({"code": 0, "msg": "", "data": demo_value})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
