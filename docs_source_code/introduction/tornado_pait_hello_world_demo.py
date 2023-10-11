from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.field import Body


class DemoHandler(RequestHandler):
    @pait()
    def post(
        self,
        uid: int = Body.t(description="user id", gt=10, lt=1000),
        username: str = Body.t(description="user name", min_length=2, max_length=4),
    ) -> None:
        self.write({"uid": uid, "user_name": username})


app: Application = Application([(r"/api", DemoHandler)])


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
