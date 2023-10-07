from typing import List

from pydantic import ValidationError
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait
from pait.exceptions import TipException
from pait.openapi.doc_route import AddDocRoute


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc

        if isinstance(exc, ValidationError):
            self.write({"data": exc.errors()})
        else:
            self.write({"data": str(exc)})
        self.finish()


class DemoHandler(_Handler):
    @pait()
    async def get(self, demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2)) -> None:
        self.write({"data": demo_value})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
