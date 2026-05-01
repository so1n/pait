import tornado.ioloop
import tornado.web

from pait.app.tornado import APIRoute

api_route = APIRoute(path="/api")


@api_route.get("/health", framework_extra_param={"route_title": "ExtraHealthHandler"})
def health() -> dict:
    return {"ok": True}


def make_app():
    app = tornado.web.Application()
    api_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
