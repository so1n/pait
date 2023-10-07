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

        self.write({"data": str(exc)})
        self.finish()


fake_db_dict: dict = {"u12345": "so1n"}


class GetUserDepend(object):
    user_name: str = field.Query.i()

    async def __call__(self, token: str = field.Header.i()) -> str:
        if token not in fake_db_dict:
            raise RuntimeError(f"Can not found by token:{token}")
        user_name = fake_db_dict[token]
        if user_name != self.user_name:
            raise RuntimeError("The specified user could not be found through the token")
        return user_name


class DemoHandler(_Handler):
    @pait()
    async def get(self, token: str = field.Depends.i(GetUserDepend)) -> None:
        self.write({"user": token})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
