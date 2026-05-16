import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from pydantic import BaseModel

from example.common import depend
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait._pydanitc_adapter import model_dump
from pait.field import Depends, Header, Json, Path, Query
from pait.mcp import MCP, MCPConfig

mcp_pait = global_pait.create_sub_pait(group="mcp")


class MCPUserPayload(BaseModel):
    name: str
    age: int


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
def mcp_user_route(uid: int = Path.i(description="user id")) -> JsonResponse:
    return JsonResponse({"uid": uid, "name": "so1n"})


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
def mcp_upsert_user_route(
    user: MCPUserPayload = Json.i(description="user payload", raw_return=True),
    notify: bool = Query.i(False, description="whether to send a notification"),
    request_id: str = Header.i("", alias="X-Request-Id", description="request id"),
) -> JsonResponse:
    return JsonResponse({"user": model_dump(user), "notify": notify, "request_id": request_id})


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
def mcp_response_route() -> JsonResponse:
    return JsonResponse({"framework": "django", "ok": True})


@mcp_pait(
    desc="Get MCP demo HTTP dispatcher status from the Django app",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_mcp_http_dispatcher_status",
            description="Get MCP demo HTTP dispatcher status from the Django app",
            call_mode="http",
            read_only=True,
        )
    },
)
def mcp_http_dispatcher_route() -> JsonResponse:
    return JsonResponse({"mcp": True, "http_dispatcher": True})


@mcp_pait(
    desc="Get MCP demo depend status from the Django app",
    extra={
        "mcp": MCPConfig(
            include=True,
            name="get_mcp_depend_status",
            description="Get MCP demo depend status from the Django app",
            read_only=True,
        )
    },
)
def mcp_depend_route(check_token: None = Depends.i(depend.CheckTokenDepend)) -> JsonResponse:
    return JsonResponse({"mcp": True, "depend": True})


@mcp_pait(desc="Private MCP demo route", extra={"mcp": MCPConfig(include=False, name="get_mcp_private_user")})
def mcp_private_route() -> dict:
    return {"ok": False}


def add_mcp_demo_route(urlpatterns: list, mcp_path: str = "/mcp") -> MCP:
    mcp = MCP(urlpatterns, mcp_path=mcp_path, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="Example app config")
    def app_config() -> dict:
        return {"name": "django-example", "version": "1.0.0"}

    return mcp


urlpatterns = [
    route_path("api/mcp/user/<int:uid>", mcp_user_route, ["GET"], name="mcp_user"),
    route_path("api/mcp/user", mcp_upsert_user_route, ["POST"], name="mcp_upsert_user"),
    route_path("api/mcp/response", mcp_response_route, ["GET"], name="mcp_response"),
    route_path("api/mcp/http-dispatcher", mcp_http_dispatcher_route, ["GET"], name="mcp_http_dispatcher"),
    route_path("api/mcp/depend", mcp_depend_route, ["GET"], name="mcp_depend"),
    route_path("api/mcp/private", mcp_private_route, ["GET"], name="mcp_private"),
]
add_mcp_demo_route(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.mcp_route_urlconf")
