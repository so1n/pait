import tornado.ioloop
import tornado.web

from pait.app.tornado import APIRoute
from pait.g import get_ctx
from pait.model.tag import Tag

api_tag = Tag("api-route-api")
users_tag = Tag("api-route-users")

parent_route = APIRoute(path="/api", group="main", append_tag=(api_tag,))
child_route = APIRoute(path="/users", tag=(users_tag,))


@child_route.get("/profile")
def get_profile(request: tornado.web.RequestHandler) -> None:
    core_model = get_ctx().pait_core_model
    request.write({"group": core_model.group, "tags": [tag.name for tag in core_model.tag]})


parent_route.include_sub_route(child_route)


def make_app():
    app = tornado.web.Application()
    parent_route.inject(app)
    return app


app = make_app()


if __name__ == "__main__":
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
