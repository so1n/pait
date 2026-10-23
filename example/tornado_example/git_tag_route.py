from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.extra.tag import GitTag
from pait.g import get_ctx

route_commit_tag = GitTag(fallback="unreleased")


class RouteVersionHandler(RequestHandler):
    @pait(tag=(route_commit_tag,))
    def get(self) -> None:
        """Return the Git tag selected from this route's source history."""
        resolved_tag = get_ctx().pait_core_model.tag[0]
        self.write({"route": "route_version", "tag": resolved_tag.name})


def create_app() -> Application:
    return Application([(r"/api/route-version", RouteVersionHandler)])


if __name__ == "__main__":
    create_app().listen(8000)
    IOLoop.current().start()
