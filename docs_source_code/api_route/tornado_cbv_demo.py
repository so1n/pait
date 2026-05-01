import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import APIRoute, pait
from pait.field import Header, Json

api_route = APIRoute(path="/api")


class UserAPIView(RequestHandler):
    def get(self, user_id: int = Header.i(alias="X-User-ID")) -> None:
        self.write({"user_id": user_id})

    @pait()
    def post(self, name: str = Json.i()) -> None:
        self.write({"created": {"name": name}})


api_route.add_cbv_route(UserAPIView, path="/users")


def make_app():
    app = tornado.web.Application()
    api_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
