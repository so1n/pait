import httpx
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.any import get_app_attribute, set_app_attribute


class DemoHandler(RequestHandler):
    async def get(self) -> None:
        client: httpx.AsyncClient = get_app_attribute(self.application, "client")
        self.write({"status_code": (await client.get("http://so1n.me")).status_code})


app: Application = Application()
app.add_handlers(".*$", [("/api/demo", DemoHandler)])
set_app_attribute(app, "client", httpx.AsyncClient())


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
