from typing import Optional

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait
from pait.exceptions import TipException
from pait.plugin.required import RequiredPlugin


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc
        self.write({"data": str(exc)})
        self.finish()


class DemoHandler(_Handler):
    @pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["user_name"]})])
    async def get(
        self,
        uid: str = field.Query.i(),
        user_name: Optional[str] = field.Query.i(default=None),
        email: Optional[str] = field.Query.i(default=None),
    ) -> None:
        self.write({"uid": uid, "user_name": user_name, "email": email})


app: Application = Application([(r"/api/demo", DemoHandler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
