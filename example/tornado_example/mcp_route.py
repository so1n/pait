from tornado.web import Application

from example.tornado_example.utils import MyHandler, global_pait
from pait.app.tornado.mcp import add_mcp_route
from pait.field import Path
from pait.mcp import AsyncMCP, MCPConfig

mcp_pait = global_pait.create_sub_pait(group="mcp")


class MCPUserHandler(MyHandler):
    @mcp_pait(
        desc="Get MCP demo user by uid",
        extra={
            "mcp": MCPConfig(
                include=True,
                name="get_mcp_demo_user",
                description="Get MCP demo user by uid",
                read_only=True,
            )
        },
    )
    async def get(self, uid: int = Path.i(description="user id")) -> None:
        self.write({"uid": uid, "name": "so1n"})


def add_mcp_demo_route(app: Application) -> AsyncMCP:
    mcp = AsyncMCP(app, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="Example app config")
    def app_config() -> dict:
        return {"name": "tornado-example", "version": "1.0.0"}

    add_mcp_route(app, mcp, path="/mcp")
    return mcp
