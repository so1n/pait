from flask import Flask, jsonify
from pydantic import BaseModel

from pait._pydanitc_adapter import model_dump
from pait.app.flask import pait
from pait.field import Header, Json, Path, Query
from pait.mcp import MCP, MCPConfig


class UserPayload(BaseModel):
    name: str
    age: int


@pait(
    desc="Get user by uid",
    extra={"mcp": MCPConfig(include=True, name="get_user", description="Get user by uid", read_only=True)},
)
def get_user(uid: int = Path.i(description="user id")) -> object:
    return jsonify({"uid": uid, "name": "so1n"})


@pait(
    desc="Create or update user",
    extra={"mcp": MCPConfig(include=True, name="upsert_user", description="Create or update user")},
)
def upsert_user(
    user: UserPayload = Json.i(description="user payload", raw_return=True),
    notify: bool = Query.i(False, description="whether to send a notification"),
    request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
) -> object:
    return jsonify({"user": model_dump(user), "notify": notify, "request_id": request_id})


app = Flask("mcp-demo")
app.add_url_rule("/users/<int:uid>", view_func=get_user, methods=["GET"])
app.add_url_rule("/users", view_func=upsert_user, methods=["POST"])
mcp = MCP(app, mcp_path="/mcp", overwrite_already_exists_data=True)


@mcp.resource("config://app", name="app-config", description="Example app config")
def app_config() -> dict:
    return {"name": "flask-mcp-demo", "version": "1.0.0"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
