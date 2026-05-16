from typing import Any

from pydantic import BaseModel
from sanic import Request, Sanic, response

from example.common import depend
from example.sanic_example.utils import global_pait
from pait._pydanitc_adapter import model_dump
from pait.field import Depends, Header, Json, Path, Query
from pait.mcp import AsyncMCP, MCPConfig

mcp_pait = global_pait.create_sub_pait(group="mcp")


class MCPUserPayload(BaseModel):
    name: str
    age: int


class MCPUserSummaryOutput(BaseModel):
    uid: int
    name: str


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
async def mcp_user_route(uid: int = Path.i(description="user id")) -> response.HTTPResponse:
    return response.json({"uid": uid, "name": "so1n"})


@mcp_pait(
    desc="Get MCP demo user summary",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_mcp_user_summary",
            description="Get MCP demo user summary",
            output_model=MCPUserSummaryOutput,
            read_only=True,
        )
    },
)
async def mcp_user_summary_route(uid: int = Path.i(description="user id")) -> response.HTTPResponse:
    return response.json({"uid": uid, "name": "so1n", "age": 18, "email": "so1n@example.com", "private_token": "token"})


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
async def mcp_upsert_user_route(
    user: MCPUserPayload = Json.i(description="user payload", raw_return=True),
    notify: bool = Query.i(False, description="whether to send a notification"),
    request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
) -> dict:
    return {"user": model_dump(user), "notify": notify, "request_id": request_id}


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
async def mcp_response_route(request: Any = None) -> response.HTTPResponse:
    return response.json({"framework": "sanic", "ok": True})


@mcp_pait(
    desc="Get MCP demo HTTP dispatcher status from the Sanic app",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_mcp_http_dispatcher_status",
            description="Get MCP demo HTTP dispatcher status from the Sanic app",
            call_mode="http",
            read_only=True,
        )
    },
)
async def mcp_http_dispatcher_route(request: Request) -> response.HTTPResponse:
    return response.json({"mcp": True, "http_dispatcher": True})


@mcp_pait(
    desc="Get MCP demo depend status from the Sanic app",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_mcp_depend_status",
            description="Get MCP demo depend status from the Sanic app",
            read_only=True,
        )
    },
)
async def mcp_depend_route(
    request: Any = None, check_token: None = Depends.i(depend.CheckTokenDepend)
) -> response.HTTPResponse:
    return response.json({"mcp": True, "depend": True})


@mcp_pait(
    desc="Private MCP demo route",
    extra={"mcp": MCPConfig(include=False, name="get_mcp_private_user")},
)
async def mcp_private_route(request: Request) -> dict:
    return {"ok": False}


def add_mcp_demo_route(app: Sanic, mcp_path: str = "/mcp") -> AsyncMCP:
    mcp = AsyncMCP(app, mcp_path=mcp_path, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="Example app config")
    def app_config() -> dict:
        return {"name": "sanic-example", "version": "1.0.0"}

    return mcp
