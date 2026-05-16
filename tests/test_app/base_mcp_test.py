import json
from typing import Any, Dict, Mapping, Optional


class BaseMCPHTTPClient(object):
    def __init__(self, client: Any, path: str = "/mcp") -> None:
        self.client = client
        self.path = path

    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        raise NotImplementedError

    def get_json(self, path: str) -> Dict[str, Any]:
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

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        return self.client.post(path, json=payload).status_code

    def get_json(self, path: str) -> Dict[str, Any]:
        return self.client.get(path).get_json() or {}


class StarletteMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, json=payload).json()

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        return self.client.post(path, json=payload).status_code

    def get_json(self, path: str) -> Dict[str, Any]:
        return self.client.get(path).json()


class SanicMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, json=payload)[1].json

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        return self.client.post(path, json=payload)[1].status_code

    def get_json(self, path: str) -> Dict[str, Any]:
        return self.client.get(path)[1].json


class TornadoMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        response = self.client.fetch(
            self.path,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
        )
        return json.loads(response.body.decode())

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        response = self.client.fetch(
            path,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
            raise_error=False,
        )
        return response.code

    def get_json(self, path: str) -> Dict[str, Any]:
        response = self.client.fetch(path)
        return json.loads(response.body.decode())


class DjangoMCPHTTPClient(BaseMCPHTTPClient):
    def _post(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.client.post(self.path, data=json.dumps(payload), content_type="application/json").json()

    def post_status(self, path: str, payload: Mapping[str, Any]) -> int:
        return self.client.post(path, data=json.dumps(payload), content_type="application/json").status_code

    def get_json(self, path: str) -> Dict[str, Any]:
        return self.client.get(path).json()


def assert_mcp_route(mcp_client: BaseMCPHTTPClient, app_name: str, support_http_dispatcher: bool = True) -> None:
    initialize_resp = mcp_client.request("initialize", {"protocolVersion": "2025-06-18"}, request_id=1)
    assert initialize_resp["jsonrpc"] == "2.0"
    assert initialize_resp["id"] == 1
    assert initialize_resp["result"]["protocolVersion"] == "2025-06-18"
    assert initialize_resp["result"]["capabilities"] == {
        "resources": {"listChanged": False},
        "tools": {"listChanged": False},
    }
    assert initialize_resp["result"]["serverInfo"] == {"name": "pait", "version": "0.0.0"}
    assert mcp_client.request("notifications/initialized") == {}

    tool_list = mcp_client.list_tools()["tools"]
    tool_dict = {tool["name"]: tool for tool in tool_list}
    expected_tool_name_set = {
        "get_mcp_demo_user",
        "get_mcp_user_summary",
        "upsert_mcp_demo_user",
        "get_mcp_demo_response",
        "get_mcp_depend_status",
    }
    if support_http_dispatcher:
        expected_tool_name_set.add("get_mcp_http_dispatcher_status")
    assert set(tool_dict) == expected_tool_name_set

    get_user_tool = tool_dict["get_mcp_demo_user"]
    assert get_user_tool["description"] == "Get MCP demo user by uid"
    assert get_user_tool["annotations"] == {"readOnlyHint": True}
    assert "path" in get_user_tool["inputSchema"]["properties"]

    user_summary_tool = tool_dict["get_mcp_user_summary"]
    assert user_summary_tool["description"] == "Get MCP demo user summary"
    assert user_summary_tool["annotations"] == {"readOnlyHint": True}
    assert set(user_summary_tool["outputSchema"]["properties"]) == {"uid", "name"}

    upsert_tool = tool_dict["upsert_mcp_demo_user"]
    assert upsert_tool["description"] == "Create or update an MCP demo user"
    assert "annotations" not in upsert_tool
    assert {"body", "query", "header"} <= set(upsert_tool["inputSchema"]["properties"])

    response_tool = tool_dict["get_mcp_demo_response"]
    assert response_tool["description"] == "Get MCP demo framework response"
    assert response_tool["annotations"] == {"readOnlyHint": True}

    if support_http_dispatcher:
        http_dispatcher_tool = tool_dict["get_mcp_http_dispatcher_status"]
        assert (
            http_dispatcher_tool["description"]
            == f"Get MCP demo HTTP dispatcher status from the {app_name.split('-', 1)[0].title()} app"
        )
        assert http_dispatcher_tool["annotations"] == {"readOnlyHint": True}

    depend_tool = tool_dict["get_mcp_depend_status"]
    assert depend_tool["description"] == f"Get MCP demo depend status from the {app_name.split('-', 1)[0].title()} app"
    assert depend_tool["annotations"] == {"readOnlyHint": True}
    assert "header" in depend_tool["inputSchema"]["properties"]

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

    original_summary_resp = mcp_client.get_json("/api/mcp/user-summary/1")
    assert original_summary_resp == {
        "uid": 1,
        "name": "so1n",
        "age": 18,
        "email": "so1n@example.com",
        "private_token": "token",
    }
    summary_resp = mcp_client.call_tool("get_mcp_user_summary", {"path": {"uid": 1}})
    assert summary_resp["isError"] is False
    assert json.loads(summary_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

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

    if support_http_dispatcher:
        http_dispatcher_resp = mcp_client.call_tool("get_mcp_http_dispatcher_status")
        assert http_dispatcher_resp["isError"] is False
        assert json.loads(http_dispatcher_resp["content"][0]["text"]) == {"mcp": True, "http_dispatcher": True}

    depend_resp = mcp_client.call_tool("get_mcp_depend_status", {"header": {"token": "demo-token"}})
    assert depend_resp["isError"] is False
    assert json.loads(depend_resp["content"][0]["text"]) == {"mcp": True, "depend": True}

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


def assert_mcp_route_with_custom_path(
    mcp_client: BaseMCPHTTPClient, app_name: str, support_http_dispatcher: bool = True
) -> None:
    assert mcp_client.post_status("/mcp", {"method": "tools/list"}) == 404
    assert_mcp_route(mcp_client, app_name, support_http_dispatcher=support_http_dispatcher)
