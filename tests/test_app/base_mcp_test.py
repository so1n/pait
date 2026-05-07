import json
from typing import Any, Dict, Mapping, Optional


class BaseMCPHTTPClient(object):
    def __init__(self, client: Any, path: str = "/mcp") -> None:
        self.client = client
        self.path = path

    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def request(
        self, method: str, params: Optional[Mapping[str, Any]] = None, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"method": method}
        if params is not None:
            payload["params"] = params
        if request_id is not None:
            payload["jsonrpc"] = "2.0"
            payload["id"] = request_id
        return self._post(payload)

    def list_tools(self) -> Dict[str, Any]:
        return self.request("tools/list")

    def call_tool(self, name: str, arguments: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"name": name, "arguments": arguments or {}}
        return self.request("tools/call", params)

    def read_resource(self, uri: str) -> Dict[str, Any]:
        return self.request("resources/read", {"uri": uri})


class FlaskMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, json=payload).get_json() or {}


class StarletteMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, json=payload).json()


class SanicMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, json=payload)[1].json


class TornadoMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        response = self.client.fetch(
            self.path,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
        )
        return json.loads(response.body.decode())


def assert_mcp_route(mcp_client: BaseMCPHTTPClient, app_name: str, support_http_tool: bool = True) -> None:
    tool_list = mcp_client.list_tools()["tools"]
    tool_dict = {tool["name"]: tool for tool in tool_list}
    expected_tool_name_set = {"get_mcp_demo_user", "upsert_mcp_demo_user", "get_mcp_demo_response"}
    if support_http_tool:
        expected_tool_name_set.add("get_mcp_redis_status")
    assert set(tool_dict) == expected_tool_name_set

    get_user_tool = tool_dict["get_mcp_demo_user"]
    assert get_user_tool["description"] == "Get MCP demo user by uid"
    assert get_user_tool["annotations"] == {"readOnlyHint": True}
    assert "path" in get_user_tool["inputSchema"]["properties"]

    upsert_tool = tool_dict["upsert_mcp_demo_user"]
    assert upsert_tool["description"] == "Create or update an MCP demo user"
    assert "annotations" not in upsert_tool
    assert {"body", "query", "header"} <= set(upsert_tool["inputSchema"]["properties"])

    response_tool = tool_dict["get_mcp_demo_response"]
    assert response_tool["description"] == "Get MCP demo framework response"
    assert response_tool["annotations"] == {"readOnlyHint": True}

    if support_http_tool:
        redis_tool = tool_dict["get_mcp_redis_status"]
        assert (
            redis_tool["description"] == f"Get MCP demo Redis status from the {app_name.split('-', 1)[0].title()} app"
        )
        assert redis_tool["annotations"] == {"readOnlyHint": True}

    call_resp = mcp_client.call_tool("get_mcp_demo_user", {"path": {"uid": 1}})
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    envelope_resp = mcp_client.request(
        "tools/call",
        {"name": "get_mcp_demo_user", "arguments": {"path": {"uid": 1}}},
        1,
    )
    assert envelope_resp["jsonrpc"] == "2.0"
    assert envelope_resp["id"] == 1
    assert json.loads(envelope_resp["result"]["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    direct_only_resp = mcp_client.request(
        "tools/call",
        {"name": "get_mcp_demo_user", "arguments": {"path": {"uid": 1}}, "callMode": "http"},
    )
    assert direct_only_resp["isError"] is False
    assert json.loads(direct_only_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    upsert_resp = mcp_client.call_tool(
        "upsert_mcp_demo_user",
        {
            "body": {"name": "appl", "age": 2},
            "query": {"notify": True},
            "header": {"X-Request-Id": "req-1"},
        },
    )
    assert upsert_resp["isError"] is False
    assert json.loads(upsert_resp["content"][0]["text"]) == {
        "user": {"name": "appl", "age": 2},
        "notify": True,
        "request_id": "req-1",
    }

    response_resp = mcp_client.call_tool("get_mcp_demo_response")
    assert response_resp["isError"] is False
    assert json.loads(response_resp["content"][0]["text"]) == {
        "framework": app_name.split("-", 1)[0],
        "ok": True,
    }

    if support_http_tool:
        redis_resp = mcp_client.call_tool("get_mcp_redis_status")
        assert redis_resp["isError"] is False
        assert json.loads(redis_resp["content"][0]["text"]) == {"redis": True, "client": "Redis"}

    private_resp = mcp_client.call_tool("get_mcp_private_user")
    assert private_resp["isError"] is True
    assert private_resp["content"][0]["text"] == "MCP tool not found: get_mcp_private_user"

    assert mcp_client.read_resource("config://app") == {
        "contents": [
            {
                "uri": "config://app",
                "mimeType": "text/plain",
                "text": json.dumps({"name": app_name, "version": "1.0.0"}),
            }
        ]
    }
