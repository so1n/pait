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
    async def get(
        self,
        demo_value1: int = field.Query.i(gt=1, lt=10),
        demo_value2: int = field.Query.i(ge=1, le=1),
        demo_value3: int = field.Query.i(multiple_of=3),
    ) -> None:
        self.write({"data": [demo_value1, demo_value2, demo_value3]})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
