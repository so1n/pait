from starlette.applications import Starlette
from starlette.responses import JSONResponse

from example.starlette_example.utils import global_pait
from pait.app.starlette.mcp import add_mcp_route
from pait.field import Path
from pait.mcp import MCP

mcp_pait = global_pait.create_sub_pait(group="mcp")


@mcp_pait(
    desc="Get MCP demo user by uid",
    extra={
        "mcp": {
            "include": True,
            "name": "get_mcp_demo_user",
            "description": "Get MCP demo user by uid",
            "read_only": True,
        }
    },
)
async def mcp_user_route(uid: int = Path.i(description="user id")) -> JSONResponse:
    return JSONResponse({"uid": uid, "name": "so1n"})


def add_mcp_demo_route(app: Starlette) -> MCP:
    mcp = MCP(app, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="Example app config")
    def app_config() -> dict:
        return {"name": "starlette-example", "version": "1.0.0"}

    add_mcp_route(app, mcp, path="/mcp")
    return mcp
