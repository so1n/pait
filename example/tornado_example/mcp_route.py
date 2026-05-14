from pydantic import BaseModel
from tornado.web import Application

from example.common import depend
from example.tornado_example.utils import MyHandler, global_pait
from pait._pydanitc_adapter import model_dump
from pait.field import Depends, Header, Json, Path, Query
from pait.mcp import AsyncMCP, MCPConfig

mcp_pait = global_pait.create_sub_pait(group="mcp")


class MCPUserPayload(BaseModel):
    name: str
    age: int


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


class MCPUpsertUserHandler(MyHandler):
    @mcp_pait(
        desc="Create or update an MCP demo user",
        extra={
            "mcp": MCPConfig(
                include=True,
                name="upsert_mcp_demo_user",
                description="Create or update an MCP demo user",
            )
        },
    )
    async def post(
        self,
        user: MCPUserPayload = Json.i(description="user payload", raw_return=True),
        notify: bool = Query.i(False, description="whether to send a notification"),
        request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
    ) -> None:
        self.write({"user": model_dump(user), "notify": notify, "request_id": request_id})


class MCPResponseHandler(MyHandler):
    @mcp_pait(
        desc="Get MCP demo framework response",
        extra={
            "mcp": MCPConfig(
                include=True,
                name="get_mcp_demo_response",
                description="Get MCP demo framework response",
                read_only=True,
            )
        },
    )
    async def get(self) -> None:
        self.write({"framework": "tornado", "ok": True})


class MCPDependHandler(MyHandler):
    @mcp_pait(
        desc="Get MCP demo depend status from the Tornado app",
        extra={
            "mcp": MCPConfig(
                include=True,
                name="get_mcp_depend_status",
                description="Get MCP demo depend status from the Tornado app",
                read_only=True,
            )
        },
    )
    async def get(self, check_token: None = Depends.i(depend.CheckTokenDepend)) -> None:
        self.write({"mcp": True, "depend": True})


class MCPPrivateHandler(MyHandler):
    @mcp_pait(
        desc="Private MCP demo route",
        extra={"mcp": MCPConfig(include=False, name="get_mcp_private_user")},
    )
    async def get(self) -> None:
        self.write({"ok": False})


def add_mcp_demo_route(app: Application, mcp_path: str = "/mcp") -> AsyncMCP:
    mcp = AsyncMCP(app, mcp_path=mcp_path, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="Example app config")
    def app_config() -> dict:
        return {"name": "tornado-example", "version": "1.0.0"}

    return mcp
