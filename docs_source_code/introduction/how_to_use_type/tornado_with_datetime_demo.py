import datetime

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait


class DemoHandler(RequestHandler):
    @pait()
    def get(self, timestamp: datetime.datetime = field.Query.i()) -> None:
        self.write({"time": timestamp.isoformat()})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
