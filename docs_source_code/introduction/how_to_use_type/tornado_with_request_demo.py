from tornado.httputil import HTTPServerRequest
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait


class DemoHandler(RequestHandler):
    @pait()
    def get(self, req: HTTPServerRequest) -> None:
        self.write({"url": req.uri, "method": req.method})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
