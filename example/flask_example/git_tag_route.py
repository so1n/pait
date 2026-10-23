from flask import Flask

from pait.app.flask import pait
from pait.extra.tag import GitTag
from pait.g import get_ctx

route_commit_tag = GitTag(fallback="unreleased")


@pait(tag=(route_commit_tag,))
def route_version() -> dict:
    """Return the Git tag selected from this route's source history."""
    resolved_tag = get_ctx().pait_core_model.tag[0]
    return {"route": "route_version", "tag": resolved_tag.name}


def create_app() -> Flask:
    app = Flask(__name__)
    app.add_url_rule("/api/route-version", view_func=route_version, methods=["GET"])
    return app


if __name__ == "__main__":
    create_app().run(port=8000)
