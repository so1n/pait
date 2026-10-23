from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from pait.app.sanic import pait
from pait.extra.tag import GitTag
from pait.g import get_ctx

route_commit_tag = GitTag(fallback="unreleased")


@pait(tag=(route_commit_tag,))
async def route_version(request: Request) -> HTTPResponse:
    """Return the Git tag selected from this route's source history."""
    resolved_tag = get_ctx().pait_core_model.tag[0]
    return json({"route": "route_version", "tag": resolved_tag.name})


def create_app() -> Sanic:
    app = Sanic("pait-git-tag-example", configure_logging=False)
    app.add_route(route_version, "/api/route-version", methods=["GET"])
    return app


if __name__ == "__main__":
    create_app().run(port=8000)
