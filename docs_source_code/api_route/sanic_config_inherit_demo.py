from sanic import Sanic
from sanic.response import json

from pait.app.sanic import APIRoute
from pait.g import get_ctx
from pait.model.tag import Tag

api_tag = Tag("api-route-api")
users_tag = Tag("api-route-users")

parent_route = APIRoute(path="/api", group="main", append_tag=(api_tag,))
child_route = APIRoute(path="/users", tag=(users_tag,))


@child_route.get("/profile")
async def get_profile():
    core_model = get_ctx().pait_core_model
    return json({"group": core_model.group, "tags": [tag.name for tag in core_model.tag]})


parent_route.include_sub_route(child_route)


def create_app() -> Sanic:
    app = Sanic("api_route_config_inherit_demo")
    parent_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
