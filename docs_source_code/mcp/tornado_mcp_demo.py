from pydantic import BaseModel
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait._pydanitc_adapter import model_dump
from pait.app.tornado import pait
from pait.field import Header, Json, Path, Query
from pait.mcp import AsyncMCP, MCPConfig


class UserPayload(BaseModel):
    name: str
    age: int


class UserHandler(RequestHandler):
    @pait(
        desc="Get user by uid",
        extra={"mcp": MCPConfig(include=True, name="get_user", description="Get user by uid", read_only=True)},
    )
    async def get(self, uid: int = Path.i(description="user id")) -> None:
        self.write({"uid": uid, "name": "so1n"})


class UpsertUserHandler(RequestHandler):
    @pait(
        desc="Create or update user",
        extra={"mcp": MCPConfig(include=True, name="upsert_user", description="Create or update user")},
    )
    async def post(
        self,
        user: UserPayload = Json.i(description="user payload", raw_return=True),
        notify: bool = Query.i(False, description="whether to send a notification"),
        request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
    ) -> None:
        self.write({"user": model_dump(user), "notify": notify, "request_id": request_id})


class PrivateUserHandler(RequestHandler):
    @pait(desc="Private route", extra={"mcp": MCPConfig(include=False, name="private_user")})
    async def get(self) -> None:
        self.write({"ok": False})


app = Application(
    [
        (r"/users/(?P<uid>\w+)", UserHandler),
        (r"/users", UpsertUserHandler),
        (r"/private-user", PrivateUserHandler),
    ]
)
mcp = AsyncMCP(app, mcp_path="/mcp", overwrite_already_exists_data=True)


@mcp.resource("config://app", name="app-config", description="Example app config")
def app_config() -> dict:
    return {"name": "tornado-mcp-demo", "version": "1.0.0"}


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
