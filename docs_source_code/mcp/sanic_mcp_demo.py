from pydantic import BaseModel
from sanic import Request, Sanic, response
from sanic.response import HTTPResponse

from pait._pydanitc_adapter import model_dump
from pait.app.sanic import pait
from pait.field import Header, Json, Path, Query
from pait.mcp import AsyncMCP, MCPConfig


class UserPayload(BaseModel):
    name: str
    age: int


@pait(
    desc="Get user by uid",
    extra={"mcp": MCPConfig(include=True, name="get_user", description="Get user by uid", read_only=True)},
)
async def get_user(uid: int = Path.i(description="user id")) -> HTTPResponse:
    return response.json({"uid": uid, "name": "so1n"})


@pait(
    desc="Create or update user",
    extra={"mcp": MCPConfig(include=True, name="upsert_user", description="Create or update user")},
)
async def upsert_user(
    user: UserPayload = Json.i(description="user payload", raw_return=True),
    notify: bool = Query.i(False, description="whether to send a notification"),
    request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
) -> HTTPResponse:
    return response.json({"user": model_dump(user), "notify": notify, "request_id": request_id})


@pait(desc="Private route", extra={"mcp": MCPConfig(include=False, name="private_user")})
async def private_user(request: Request) -> HTTPResponse:
    return response.json({"ok": False})


@pait(
    desc="Get framework response through HTTP call mode",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_http_status",
            description="Get framework response through HTTP call mode",
            call_mode="http",
            read_only=True,
        )
    },
)
async def get_http_status(request: Request) -> HTTPResponse:
    return response.json({"mcp": True, "call_mode": "http", "path": request.path})


app = Sanic(name="sanic_mcp_demo", configure_logging=False)
app.add_route(get_user, "/users/<uid:int>", methods=["GET"])
app.add_route(upsert_user, "/users", methods=["POST"])
app.add_route(private_user, "/private-user", methods=["GET"])
app.add_route(get_http_status, "/mcp/http-status", methods=["GET"])
mcp = AsyncMCP(app, mcp_path="/mcp", overwrite_already_exists_data=True)


@mcp.resource("config://app", name="app-config", description="Example app config")
def app_config() -> dict:
    return {"name": "sanic-mcp-demo", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
