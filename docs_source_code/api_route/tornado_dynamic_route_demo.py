import tornado.ioloop
import tornado.web

from pait.app.tornado import APIRoute
from pait.field import Json

api_route = APIRoute(path="/api")


def greet(name: str = Json.i()) -> dict:
    return {"message": f"Hello {name}"}


api_route.add_api_route(greet, method=["POST"], path="/greet", desc="Greeting API")


def make_app():
    app = tornado.web.Application()
    api_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
