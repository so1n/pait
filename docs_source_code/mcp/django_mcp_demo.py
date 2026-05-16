import os
import sys
from typing import Any, Dict, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.field import Json, Path
from pait.mcp import MCP, MCPConfig


@pait(extra={"mcp": MCPConfig(include=True, name="get_user", read_only=True)})
def get_user(uid: int = Path.i()) -> JsonResponse:
    return JsonResponse({"uid": uid, "name": "so1n"})


@pait(extra={"mcp": MCPConfig(include=True, name="create_user", call_mode="http")})
def create_user(name: str = Json.i(), age: int = Json.i()) -> JsonResponse:
    return JsonResponse({"name": name, "age": age})


urlpatterns: List[Any] = [
    route_path("api/user/<int:uid>", get_user, ["GET"], name="get_user"),
    route_path("api/user", create_user, ["POST"], name="create_user"),
]

mcp = MCP(urlpatterns, mcp_path="/mcp")


@mcp.resource("resource://app")
def app_resource() -> Dict[str, str]:
    return {"name": "django-demo"}


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.mcp.django_mcp_demo_urlconf")
