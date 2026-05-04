import asyncio
import json
from contextlib import contextmanager
from typing import Any, Callable, Generator, List, Mapping, Tuple

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sanic import Sanic
from starlette.applications import Starlette
from starlette.routing import Route
from tornado.web import Application

from example.flask_example.mcp_route import add_mcp_demo_route as add_flask_mcp_demo_route
from example.flask_example.mcp_route import mcp_user_route as flask_mcp_user_route
from example.sanic_example.mcp_route import add_mcp_demo_route as add_sanic_mcp_demo_route
from example.sanic_example.mcp_route import mcp_user_route as sanic_mcp_user_route
from example.starlette_example.mcp_route import add_mcp_demo_route as add_starlette_mcp_demo_route
from example.starlette_example.mcp_route import mcp_user_route as starlette_mcp_user_route
from example.tornado_example.mcp_route import MCPUserHandler
from example.tornado_example.mcp_route import add_mcp_demo_route as add_tornado_mcp_demo_route
from pait import field
from pait.app.flask import load_app as flask_load_app
from pait.app.flask import pait
from pait.app.flask.mcp import add_mcp_route
from pait.app.flask.plugin.unified_response import UnifiedResponsePlugin
from pait.mcp import MCP
from pait.mcp.dispatcher import MCPDirectResponse


@contextmanager
def flask_client_ctx(app: Flask) -> Generator[FlaskClient, None, None]:
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    try:
        yield client
    finally:
        ctx.pop()


def test_mcp_tools_list_and_call() -> None:
    app = Flask(__name__)

    @app.get("/user/<int:uid>")
    @pait(
        desc="Get user detail by uid",
        plugin_list=[UnifiedResponsePlugin.build()],
        extra={
            "mcp": {
                "include": True,
                "name": "get_user",
                "description": "Get user detail by uid",
            }
        },
    )
    def get_user(uid: int = field.Path.i()) -> dict:
        return {"uid": uid, "name": "so1n"}

    @app.get("/private")
    @pait()
    def private_route() -> dict:
        return {"ok": True}

    mcp = MCP(app, overwrite_already_exists_data=True)
    add_mcp_route(app, mcp)

    with flask_client_ctx(app) as client:
        tools_resp = client.post("/mcp", json={"method": "tools/list"}).get_json()
        assert tools_resp == {
            "tools": [
                {
                    "name": "get_user",
                    "description": "Get user detail by uid",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "object",
                                "properties": {
                                    "uid": {"title": "Uid", "type": "integer"},
                                },
                                "additionalProperties": False,
                                "required": ["uid"],
                            },
                        },
                        "additionalProperties": False,
                        "required": ["path"],
                    },
                }
            ]
        }

        call_resp = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "get_user",
                    "arguments": {"path": {"uid": 1}},
                },
            },
        ).get_json()
        assert call_resp is not None
        assert call_resp["isError"] is False
        assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_constructor_reject_invalid_call_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        MCP(call_mode="invalid")
    assert "call_mode" in str(exc_info.value)


def test_mcp_without_app_can_use_resources() -> None:
    mcp = MCP()

    @mcp.resource("config://standalone", name="standalone-config", description="Standalone config")
    def standalone_config() -> dict:
        return {"name": "standalone"}

    assert mcp.list_tools() == {"tools": []}
    assert mcp.list_resources() == {
        "resources": [
            {
                "uri": "config://standalone",
                "name": "standalone-config",
                "description": "Standalone config",
                "mimeType": "text/plain",
            }
        ]
    }
    read_resp = asyncio.run(mcp.read_resource("config://standalone"))
    assert read_resp["contents"][0]["text"] == json.dumps({"name": "standalone"})


def test_mcp_constructor_accept_load_app_dispatcher_and_encoder() -> None:
    app = Flask(__name__)
    load_app_kwargs_dict = {}

    @app.get("/user/<int:uid>")
    @pait(
        extra={
            "mcp": {
                "include": True,
                "name": "get_user_with_custom_dispatcher",
            }
        },
    )
    def get_user(uid: int = field.Path.i()) -> dict:
        return {"uid": uid, "name": "so1n"}

    def custom_load_app(_app: Flask, **kwargs: Any) -> Mapping:
        load_app_kwargs_dict.update(kwargs)
        return flask_load_app(_app, **kwargs)

    async def custom_direct_dispatcher(core_model: Any, arguments: Mapping) -> MCPDirectResponse:
        return MCPDirectResponse({"operation_id": core_model.operation_id, "arguments": arguments})

    def custom_content_encoder(value: Any) -> str:
        if isinstance(value, MCPDirectResponse):
            return "custom:" + json.dumps(value.value)
        return str(value)

    mcp = MCP(
        app,
        load_app=custom_load_app,
        direct_dispatcher=custom_direct_dispatcher,
        content_encoder=custom_content_encoder,
        overwrite_already_exists_data=True,
    )

    assert load_app_kwargs_dict == {"overwrite_already_exists_data": True}
    call_resp = asyncio.run(mcp.call_tool("get_user_with_custom_dispatcher", {"path": {"uid": 1}}))
    assert call_resp["isError"] is False
    assert call_resp["content"][0]["text"].startswith("custom:")
    payload = json.loads(call_resp["content"][0]["text"][len("custom:") :])
    assert payload["arguments"] == {"path": {"uid": 1}}


def test_mcp_direct_call_mode_without_unified_response_plugin() -> None:
    app = Flask(__name__)

    @app.get("/user/<int:uid>")
    @pait(
        desc="Get user detail by uid",
        extra={
            "mcp": {
                "include": True,
                "name": "get_user_without_unified_response",
            }
        },
    )
    def get_user(uid: int = field.Path.i()) -> dict:
        return {"uid": uid, "name": "so1n"}

    mcp = MCP(app, overwrite_already_exists_data=True)
    call_resp = asyncio.run(mcp.call_tool("get_user_without_unified_response", {"path": {"uid": 1}}))
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_resource() -> None:
    app = Flask(__name__)
    mcp = MCP(app, overwrite_already_exists_data=True)

    @mcp.resource("config://app", name="app-config", description="App config")
    def app_config() -> dict:
        return {"name": "demo", "version": "1.0.0"}

    add_mcp_route(app, mcp)
    with flask_client_ctx(app) as client:
        list_resp = client.post("/mcp", json={"method": "resources/list"}).get_json()
        assert list_resp == {
            "resources": [
                {
                    "uri": "config://app",
                    "name": "app-config",
                    "description": "App config",
                    "mimeType": "text/plain",
                }
            ]
        }

        read_resp = client.post(
            "/mcp",
            json={
                "method": "resources/read",
                "params": {"uri": "config://app"},
            },
        ).get_json()
        assert read_resp == {
            "contents": [
                {
                    "uri": "config://app",
                    "mimeType": "text/plain",
                    "text": json.dumps({"name": "demo", "version": "1.0.0"}),
                }
            ]
        }


def test_mcp_http_call_mode_via_mcp_route() -> None:
    app = Flask(__name__)
    app.add_url_rule("/api/mcp/user/<int:uid>", view_func=flask_mcp_user_route, methods=["GET"])
    mcp = MCP(app, call_mode="http", overwrite_already_exists_data=True)
    add_mcp_route(app, mcp)

    with flask_client_ctx(app) as client:
        call_resp = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "get_mcp_demo_user",
                    "arguments": {"path": {"uid": 1}},
                },
            },
        ).get_json()
        assert call_resp is not None
        assert call_resp["isError"] is False
        assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_http_error_response_is_mcp_error() -> None:
    app = Flask(__name__)

    @app.get("/failed")
    @pait(
        extra={
            "mcp": {
                "include": True,
                "name": "failed_tool",
            }
        },
    )
    def failed_route() -> tuple:
        return {"message": "failed"}, 400

    mcp = MCP(app, call_mode="http", overwrite_already_exists_data=True)
    call_resp = asyncio.run(mcp.call_tool("failed_tool", {}))
    assert call_resp["isError"] is True
    assert json.loads(call_resp["content"][0]["text"]) == {"message": "failed"}


def test_mcp_direct_example_for_all_frameworks() -> None:
    flask_app = Flask("mcp-flask-example")
    flask_app.add_url_rule("/api/mcp/user/<int:uid>", view_func=flask_mcp_user_route, methods=["GET"])

    starlette_app = Starlette(routes=[Route("/api/mcp/user/{uid}", starlette_mcp_user_route, methods=["GET"])])

    sanic_app = Sanic(name="mcp-sanic-example")
    sanic_app.add_route(sanic_mcp_user_route, "/api/mcp/user/<uid:int>", methods=["GET"])

    tornado_app = Application([(r"/api/mcp/user/(?P<uid>\w+)", MCPUserHandler)])

    app_list: List[Tuple[object, Callable]] = [
        (flask_app, add_flask_mcp_demo_route),
        (starlette_app, add_starlette_mcp_demo_route),
        (sanic_app, add_sanic_mcp_demo_route),
        (tornado_app, add_tornado_mcp_demo_route),
    ]

    for app, add_mcp_demo_route in app_list:
        mcp = add_mcp_demo_route(app)  # type: ignore[arg-type]
        assert [tool["name"] for tool in mcp.list_tools()["tools"]] == ["get_mcp_demo_user"]
        call_resp = asyncio.run(mcp.call_tool("get_mcp_demo_user", {"path": {"uid": 1}}))
        assert call_resp["isError"] is False
        assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_http_call_mode_for_wsgi_asgi_frameworks() -> None:
    flask_app = Flask("mcp-flask-http-example")
    flask_app.add_url_rule("/api/mcp/user/<int:uid>", view_func=flask_mcp_user_route, methods=["GET"])

    starlette_app = Starlette(routes=[Route("/api/mcp/user/{uid}", starlette_mcp_user_route, methods=["GET"])])

    sanic_app = Sanic(name="mcp-sanic-http-example")
    sanic_app.add_route(sanic_mcp_user_route, "/api/mcp/user/<uid:int>", methods=["GET"])

    app_list: List[object] = [flask_app, starlette_app, sanic_app]

    for app in app_list:
        mcp = MCP(app, call_mode="http", overwrite_already_exists_data=True)
        assert [tool["name"] for tool in mcp.list_tools()["tools"]] == ["get_mcp_demo_user"]

        call_resp = asyncio.run(mcp.call_tool("get_mcp_demo_user", {"path": {"uid": 1}}))
        assert call_resp["isError"] is False
        assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}
