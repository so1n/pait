from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.app.starlette import pait
from pait.extra.tag import GitTag
from pait.g import get_ctx

route_commit_tag = GitTag(fallback="unreleased")


@pait(tag=(route_commit_tag,))
async def route_version(request: Request) -> JSONResponse:
    """Return the Git tag selected from this route's source history."""
    resolved_tag = get_ctx().pait_core_model.tag[0]
    return JSONResponse({"route": "route_version", "tag": resolved_tag.name})


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/api/route-version", route_version, methods=["GET"])
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), port=8000)
