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

    def call_tool(
        self, name: str, arguments: Optional[Mapping[str, Any]] = None, call_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"name": name, "arguments": arguments or {}}
        if call_mode:
            params["callMode"] = call_mode
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


def assert_mcp_route(mcp_client: BaseMCPHTTPClient, app_name: str) -> None:
    tool_list = mcp_client.list_tools()["tools"]
    assert len(tool_list) == 1
    assert tool_list[0]["name"] == "get_mcp_demo_user"
    assert tool_list[0]["description"] == "Get MCP demo user by uid"
    assert "path" in tool_list[0]["inputSchema"]["properties"]

    call_resp = mcp_client.call_tool("get_mcp_demo_user", {"path": {"uid": 1}})
    assert call_resp["isError"] is False
    assert json.loads(call_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    assert mcp_client.read_resource("config://app") == {
        "contents": [
            {
                "uri": "config://app",
                "mimeType": "text/plain",
                "text": json.dumps({"name": app_name, "version": "1.0.0"}),
            }
        ]
    }
