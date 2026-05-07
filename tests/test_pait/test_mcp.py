import json
from typing import Any, Dict, Mapping, Optional, cast

import pytest

from pait import field
from pait.app.base import BaseAppHelper
from pait.extra.config import MatchRule, apply_mcp_config
from pait.mcp import MCP, AsyncMCP, MCPCallMode, MCPConfig
from pait.mcp.dispatcher import MCPDirectResponse, dispatch_sync_tool, dispatch_tool, encode_content
from pait.mcp.http import MCPHTTPResponse, build_http_request
from pait.mcp.tool import get_mcp_config
from pait.model.core import PaitCoreModel
from pait.model.tag import Tag
from pait.param_handle import ParamHandler
from tests.conftest import fixture_loop


class FakeApp(object):
    pass


class AsyncMCPClient(object):
    def __init__(self, mcp: AsyncMCP) -> None:
        self.mcp = mcp

    async def request(
        self, method: str, params: Optional[Mapping[str, Any]] = None, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        message: Dict[str, Any] = {"method": method}
        if params is not None:
            message["params"] = params
        if request_id is not None:
            message["jsonrpc"] = "2.0"
            message["id"] = request_id
        return await self.mcp.handle_message(message)

    async def list_tools(self) -> Dict[str, Any]:
        return await self.request("tools/list")

    async def call_tool(self, name: str, arguments: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"name": name, "arguments": arguments or {}}
        return await self.request("tools/call", params)

    async def list_resources(self) -> Dict[str, Any]:
        return await self.request("resources/list")

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        return await self.request("resources/read", {"uri": uri})


class MCPClient(object):
    def __init__(self, mcp: MCP) -> None:
        self.mcp = mcp

    def request(
        self, method: str, params: Optional[Mapping[str, Any]] = None, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        message: Dict[str, Any] = {"method": method}
        if params is not None:
            message["params"] = params
        if request_id is not None:
            message["jsonrpc"] = "2.0"
            message["id"] = request_id
        return self.mcp.handle_message(message)

    def list_tools(self) -> Dict[str, Any]:
        return self.request("tools/list")

    def call_tool(self, name: str, arguments: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"name": name, "arguments": arguments or {}}
        return self.request("tools/call", params)

    def list_resources(self) -> Dict[str, Any]:
        return self.request("resources/list")

    def read_resource(self, uri: str) -> Dict[str, Any]:
        return self.request("resources/read", {"uri": uri})


def build_core_model(
    func: Any,
    *,
    name: str = "get_user",
    description: str = "Get user detail by uid",
    include: Optional[bool] = True,
    path: str = "/user/{uid}",
    operation_id: str = "get_user",
    tag: Optional[tuple] = None,
    mcp_config: Optional[MCPConfig] = None,
) -> PaitCoreModel:
    extra: Dict[str, Any] = {}
    if mcp_config is not None:
        extra["mcp"] = mcp_config
    elif include is True:
        extra["mcp"] = MCPConfig(include=True, name=name, description=description)
    elif include is False:
        extra["mcp"] = MCPConfig(include=False, name=name, description=description)

    core_model_kwargs: Dict[str, Any] = {}
    if extra:
        core_model_kwargs["extra"] = extra

    core_model = PaitCoreModel(
        func,
        BaseAppHelper,
        ParamHandler,
        path=path,
        openapi_path=path,
        method_set={"GET"},
        operation_id=operation_id,
        desc=description,
        tag=tag,
        **core_model_kwargs,
    )
    core_model.build()
    return core_model


def build_mcp(
    core_model_dict: Dict[str, PaitCoreModel],
    *,
    mcp_class: Any = AsyncMCP,
    call_mode: MCPCallMode = "direct",
    direct_dispatcher: Optional[Any] = None,
    http_dispatcher: Optional[Any] = None,
    content_encoder: Any = encode_content,
    load_app_kwargs_dict: Optional[Dict[str, Any]] = None,
) -> Any:
    if direct_dispatcher is None:
        direct_dispatcher = dispatch_sync_tool if mcp_class is MCP else dispatch_tool

    def fake_load_app(app: FakeApp, **kwargs: Any) -> Dict[str, PaitCoreModel]:
        if load_app_kwargs_dict is not None:
            load_app_kwargs_dict.update(kwargs)
        return core_model_dict

    return mcp_class(
        FakeApp(),
        load_app=fake_load_app,
        call_mode=call_mode,
        direct_dispatcher=direct_dispatcher,
        http_dispatcher=http_dispatcher,
        content_encoder=content_encoder,
        mcp_path=None,
        overwrite_already_exists_data=True,
    )


def user_route(uid: int = field.Path.i(description="user id")) -> dict:
    return {"uid": uid, "name": "so1n"}


def private_route() -> dict:
    return {"ok": True}


def tagged_route(uid: int = field.Path.i(description="user id")) -> dict:
    return {"uid": uid, "source": "tagged"}


def unnamed_mcp_route() -> dict:
    return {"ok": True}


def test_mcp_tools_list_and_call() -> None:
    mcp = build_mcp(
        {
            "user": build_core_model(user_route),
            "private": build_core_model(private_route, include=False),
        }
    )
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        tool_list = loop.run_until_complete(client.list_tools())
        assert tool_list == {
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
                                    "uid": {"title": "Uid", "description": "user id", "type": "integer"},
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

        call_resp = loop.run_until_complete(client.call_tool("get_user", {"path": {"uid": 1}}))
        assert call_resp["isError"] is False
        assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_tool_read_only_annotation() -> None:
    mcp = build_mcp(
        {
            "read": build_core_model(
                user_route,
                mcp_config=MCPConfig(include=True, name="read_user", read_only=True),
            ),
            "write": build_core_model(
                private_route,
                mcp_config=MCPConfig(include=True, name="write_user"),
                path="/user",
                operation_id="write_user",
            ),
        }
    )
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        tool_list = loop.run_until_complete(client.list_tools())

    tool_dict = {tool["name"]: tool for tool in tool_list["tools"]}
    assert tool_dict["read_user"]["annotations"] == {"readOnlyHint": True}
    assert "annotations" not in tool_dict["write_user"]


@pytest.mark.parametrize("mcp_class", [AsyncMCP, MCP])
def test_mcp_constructor_reject_invalid_call_mode(mcp_class: Any) -> None:
    with pytest.raises(ValueError) as exc_info:
        mcp_class(call_mode="invalid")
    assert "call_mode" in str(exc_info.value)


def test_mcp_without_app_can_use_resources() -> None:
    mcp = AsyncMCP()
    client = AsyncMCPClient(mcp)

    @mcp.resource("config://standalone", name="standalone-config", description="Standalone config")
    def standalone_config() -> dict:
        return {"name": "standalone"}

    with fixture_loop(mock_close_loop=True) as loop:
        assert loop.run_until_complete(client.list_tools()) == {"tools": []}
        assert loop.run_until_complete(client.list_resources()) == {
            "resources": [
                {
                    "uri": "config://standalone",
                    "name": "standalone-config",
                    "description": "Standalone config",
                    "mimeType": "text/plain",
                }
            ]
        }
        read_resp = loop.run_until_complete(client.read_resource("config://standalone"))
        assert read_resp["contents"][0]["text"] == json.dumps({"name": "standalone"})


def test_mcp_constructor_accept_load_app_dispatcher_and_encoder() -> None:
    load_app_kwargs_dict: Dict[str, Any] = {}

    async def custom_direct_dispatcher(core_model: PaitCoreModel, arguments: Mapping) -> MCPDirectResponse:
        return MCPDirectResponse({"operation_id": core_model.operation_id, "arguments": arguments})

    def custom_content_encoder(value: Any) -> str:
        if isinstance(value, MCPDirectResponse):
            return "custom:" + json.dumps(value.value)
        return str(value)

    mcp = build_mcp(
        {"user": build_core_model(user_route, name="get_user_with_custom_dispatcher")},
        direct_dispatcher=custom_direct_dispatcher,
        content_encoder=custom_content_encoder,
        load_app_kwargs_dict=load_app_kwargs_dict,
    )
    client = AsyncMCPClient(mcp)

    assert load_app_kwargs_dict == {"overwrite_already_exists_data": True}
    with fixture_loop(mock_close_loop=True) as loop:
        call_resp = loop.run_until_complete(client.call_tool("get_user_with_custom_dispatcher", {"path": {"uid": 1}}))
    assert call_resp["isError"] is False
    assert call_resp["content"][0]["text"].startswith("custom:")
    payload = json.loads(call_resp["content"][0]["text"][len("custom:") :])
    assert payload["arguments"] == {"path": {"uid": 1}}


def test_mcp_resource() -> None:
    mcp = build_mcp({})
    client = AsyncMCPClient(mcp)

    @mcp.resource("config://app", name="app-config", description="App config")
    def app_config() -> dict:
        return {"name": "demo", "version": "1.0.0"}

    with fixture_loop(mock_close_loop=True) as loop:
        assert loop.run_until_complete(client.list_resources()) == {
            "resources": [
                {
                    "uri": "config://app",
                    "name": "app-config",
                    "description": "App config",
                    "mimeType": "text/plain",
                }
            ]
        }

        read_resp = loop.run_until_complete(client.read_resource("config://app"))
    assert read_resp == {
        "contents": [
            {
                "uri": "config://app",
                "mimeType": "text/plain",
                "text": json.dumps({"name": "demo", "version": "1.0.0"}),
            }
        ]
    }


def test_async_mcp_can_read_async_resource() -> None:
    mcp = build_mcp({})
    client = AsyncMCPClient(mcp)

    @mcp.resource("config://async", name="async-config")
    async def async_config() -> dict:
        return {"name": "async"}

    with fixture_loop(mock_close_loop=True) as loop:
        read_resp = loop.run_until_complete(client.read_resource("config://async"))

    assert read_resp["contents"][0]["text"] == json.dumps({"name": "async"})


def test_mcp_handle_message_tool_call() -> None:
    mcp = build_mcp({"user": build_core_model(user_route)})
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        call_resp = loop.run_until_complete(client.call_tool("get_user", {"path": {"uid": 1}}))
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_mcp_handle_message_json_rpc_envelope() -> None:
    mcp = build_mcp({"user": build_core_model(user_route)})
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        resp = loop.run_until_complete(client.request("tools/list", request_id=1))
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert [tool["name"] for tool in resp["result"]["tools"]] == ["get_user"]


def test_mcp_unknown_tool_and_method_errors() -> None:
    mcp = build_mcp({})
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        call_resp = loop.run_until_complete(client.call_tool("missing_tool", {}))
    assert call_resp == {
        "content": [{"type": "text", "text": "MCP tool not found: missing_tool"}],
        "isError": True,
    }

    with fixture_loop(mock_close_loop=True) as loop:
        method_resp = loop.run_until_complete(client.request("missing/method", request_id=1))
    assert method_resp["id"] == 1
    assert method_resp["error"]["code"] == -32000
    assert "Unsupported MCP method" in method_resp["error"]["message"]


def test_mcp_message_params_must_be_mapping() -> None:
    mcp = build_mcp({})
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        resp = loop.run_until_complete(
            client.request("tools/list", params=["invalid"], request_id=1)  # type: ignore[arg-type]
        )

    assert resp["id"] == 1
    assert resp["error"]["code"] == -32000
    assert resp["error"]["message"] == "MCP params must be a mapping"


def test_mcp_missing_resource_returns_error() -> None:
    mcp = build_mcp({})
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        resp = loop.run_until_complete(client.request("resources/read", {"uri": "config://missing"}, request_id=1))

    assert resp["id"] == 1
    assert resp["error"]["code"] == -32000
    assert "MCP resource not found: config://missing" in resp["error"]["message"]


def test_mcp_http_error_response_is_mcp_error() -> None:
    async def fake_http_dispatcher(app: FakeApp, core_model: PaitCoreModel, arguments: Mapping) -> MCPHTTPResponse:
        return MCPHTTPResponse(400, {}, json.dumps({"message": "failed"}).encode())

    mcp = build_mcp(
        {"failed": build_core_model(private_route, name="failed_tool", path="/failed", operation_id="failed_tool")},
        call_mode="http",
        http_dispatcher=fake_http_dispatcher,
    )
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        call_resp = loop.run_until_complete(client.call_tool("failed_tool", {}))
    assert call_resp["isError"] is True
    assert json.loads(call_resp["content"][0]["text"]) == {"message": "failed"}


def test_mcp_tool_call_mode_param_does_not_override_server_config() -> None:
    async def fake_http_dispatcher(app: FakeApp, core_model: PaitCoreModel, arguments: Mapping) -> MCPHTTPResponse:
        return MCPHTTPResponse(200, {}, json.dumps({"mode": "http"}).encode())

    mcp = build_mcp(
        {"user": build_core_model(user_route)},
        http_dispatcher=fake_http_dispatcher,
    )
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        call_resp = loop.run_until_complete(
            client.request(
                "tools/call",
                {"name": "get_user", "arguments": {"path": {"uid": 1}}, "callMode": "http"},
            )
        )

    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}


def test_async_mcp_route_call_mode_overrides_default() -> None:
    async def fake_http_dispatcher(app: FakeApp, core_model: PaitCoreModel, arguments: Mapping) -> MCPHTTPResponse:
        return MCPHTTPResponse(200, {}, json.dumps({"mode": "http", "arguments": arguments}).encode())

    mcp = build_mcp(
        {
            "user": build_core_model(user_route),
            "http": build_core_model(
                private_route,
                mcp_config=MCPConfig(include=True, name="http_tool", call_mode="http"),
                path="/http",
                operation_id="http_tool",
            ),
        },
        http_dispatcher=fake_http_dispatcher,
    )
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        direct_resp = loop.run_until_complete(client.call_tool("get_user", {"path": {"uid": 1}}))
        http_resp = loop.run_until_complete(client.call_tool("http_tool", {"query": {"uid": 1}}))

    assert direct_resp["isError"] is False
    assert json.loads(direct_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}
    assert http_resp["isError"] is False
    assert json.loads(http_resp["content"][0]["text"]) == {"mode": "http", "arguments": {"query": {"uid": 1}}}


def test_mcp_duplicate_tool_names_are_renamed() -> None:
    first_model = build_core_model(private_route, name="duplicate_tool", operation_id="first_tool")
    second_model = build_core_model(user_route, name="duplicate_tool", operation_id="second_tool")
    mcp = build_mcp({"first": first_model, "second": second_model})
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        assert [tool["name"] for tool in loop.run_until_complete(client.list_tools())["tools"]] == [
            "duplicate_tool",
            "duplicate_tool_2",
        ]


def test_mcp_config_model_and_apply_by_tag() -> None:
    mcp_tag = Tag("mcp-auto-config")
    core_model = build_core_model(
        tagged_route,
        include=None,
        tag=(mcp_tag,),
        path="/tagged/{uid}",
        operation_id="tagged_route",
    )
    assert core_model.extra == {}
    assert get_mcp_config(core_model) == MCPConfig()

    apply_mcp_config(
        MCPConfig(include=True, name="tagged_tool", description="Tool configured by tag"),
        MatchRule(key="tag", target=mcp_tag),
    )(core_model)

    mcp_config = get_mcp_config(core_model)
    assert mcp_config == MCPConfig(include=True, name="tagged_tool", description="Tool configured by tag")

    mcp = build_mcp({"tagged": core_model})
    client = AsyncMCPClient(mcp)
    with fixture_loop(mock_close_loop=True) as loop:
        tools_resp = loop.run_until_complete(client.list_tools())
        call_resp = loop.run_until_complete(client.call_tool("tagged_tool", {"path": {"uid": 1}}))

    assert [tool["name"] for tool in tools_resp["tools"]] == ["tagged_tool"]
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "source": "tagged"}


def test_mcp_config_uses_route_name_and_desc_when_empty() -> None:
    core_model = build_core_model(
        unnamed_mcp_route,
        description="Route description",
        operation_id="custom_operation_id",
        mcp_config=MCPConfig(include=True),
    )
    mcp = build_mcp({"unnamed": core_model})
    client = AsyncMCPClient(mcp)

    with fixture_loop(mock_close_loop=True) as loop:
        tools_resp = loop.run_until_complete(client.list_tools())

    assert tools_resp["tools"][0]["name"] == "unnamed_mcp_route"
    assert tools_resp["tools"][0]["description"] == "Route description"


def test_mcp_config_reject_invalid_call_mode() -> None:
    with pytest.raises(ValueError) as exc_info:
        build_mcp(
            {
                "invalid": build_core_model(
                    private_route,
                    mcp_config=MCPConfig(include=True, name="invalid_tool", call_mode=cast(Any, "invalid")),
                )
            }
        )
    assert "call_mode" in str(exc_info.value)


def test_build_http_request_from_mcp_arguments() -> None:
    request = build_http_request(
        build_core_model(
            private_route,
            name="upsert_user",
            path="/user/{uid}",
            operation_id="upsert_user",
        ),
        {
            "path": {"uid": "a b"},
            "query": {"notify": True, "tag": ["a", "b"]},
            "header": {"X-Request-Id": "req-1"},
            "cookie": {"session": "token"},
            "body": {"name": "appl"},
        },
    )

    assert request.method == "GET"
    assert request.path == "/user/a%20b"
    assert request.query_string == "notify=True&tag=a&tag=b"
    assert request.headers == {
        "x-request-id": "req-1",
        "cookie": "session=token",
        "content-type": "application/json",
    }
    assert json.loads(request.body.decode()) == {"name": "appl"}


def test_build_http_request_form_takes_precedence_over_body() -> None:
    request = build_http_request(
        build_core_model(private_route, name="submit_form", path="/form", operation_id="submit_form"),
        {
            "form": {"name": "appl"},
            "body": {"ignored": True},
        },
    )

    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert request.body == b"name=appl"


def test_build_http_request_requires_all_path_arguments() -> None:
    with pytest.raises(KeyError) as exc_info:
        build_http_request(
            build_core_model(private_route, name="get_user", path="/user/{uid}", operation_id="get_user"),
            {},
        )

    assert "Missing MCP path arguments" in str(exc_info.value)


def test_sync_mcp_methods() -> None:
    mcp = build_mcp({"user": build_core_model(user_route)}, mcp_class=MCP)
    client = MCPClient(mcp)

    call_resp = client.call_tool("get_user", {"path": {"uid": 1}})
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    @mcp.resource("config://sync", name="sync-config", description="Sync config")
    def sync_config() -> dict:
        return {"name": "sync"}

    read_resp = client.read_resource("config://sync")
    assert read_resp["contents"][0]["text"] == json.dumps({"name": "sync"})

    message_resp = client.request("tools/list", request_id=1)
    assert message_resp["id"] == 1
    assert [tool["name"] for tool in message_resp["result"]["tools"]] == ["get_user"]
    assert client.list_resources() == mcp.list_resources()


def test_sync_mcp_can_use_sync_dispatcher_and_http_dispatcher() -> None:
    def custom_direct_dispatcher(core_model: PaitCoreModel, arguments: Mapping) -> MCPDirectResponse:
        return dispatch_sync_tool(core_model, arguments)

    def fake_http_dispatcher(app: FakeApp, core_model: PaitCoreModel, arguments: Mapping) -> MCPHTTPResponse:
        return MCPHTTPResponse(200, {}, json.dumps({"mode": "http", "arguments": arguments}).encode())

    mcp = build_mcp(
        {
            "user": build_core_model(user_route),
            "http": build_core_model(
                private_route,
                mcp_config=MCPConfig(include=True, name="http_tool", call_mode="http"),
                path="/http",
                operation_id="http_tool",
            ),
        },
        mcp_class=MCP,
        direct_dispatcher=custom_direct_dispatcher,
        http_dispatcher=fake_http_dispatcher,
    )
    client = MCPClient(mcp)

    direct_resp = client.call_tool("get_user", {"path": {"uid": 1}})
    assert direct_resp["isError"] is False
    assert json.loads(direct_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    http_resp = client.call_tool("http_tool", {"path": {"uid": 1}})
    assert http_resp["isError"] is False
    assert json.loads(http_resp["content"][0]["text"]) == {"mode": "http", "arguments": {"path": {"uid": 1}}}
