from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait import field
from pait.app.tornado import pait
from pait.openapi.doc_route import AddDocRoute


class DemoHandler(RequestHandler):
    @pait()
    async def get(self, content_type: str = field.Header.t(alias="Content-Type")) -> None:
        self.write(content_type)


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
