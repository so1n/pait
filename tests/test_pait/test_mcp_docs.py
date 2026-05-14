import json
from typing import Any, Dict, Mapping, Optional

from tests.conftest import fixture_loop


async def _async_request(mcp: Any, method: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    message: Dict[str, Any] = {"method": method}
    if params is not None:
        message["params"] = params
    return await mcp.handle_message(message)


def _sync_request(mcp: Any, method: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    message: Dict[str, Any] = {"method": method}
    if params is not None:
        message["params"] = params
    return mcp.handle_message(message)


def test_starlette_mcp_doc_example() -> None:
    from docs_source_code.mcp import starlette_mcp_demo

    with fixture_loop(mock_close_loop=True) as loop:
        tool_list = loop.run_until_complete(_async_request(starlette_mcp_demo.mcp, "tools/list"))
        tool_dict = {tool["name"]: tool for tool in tool_list["tools"]}

        assert set(tool_dict) == {"get_user", "upsert_user", "get_http_status"}
        assert "private_user" not in tool_dict
        assert tool_dict["get_user"]["annotations"] == {"readOnlyHint": True}
        assert "body" in tool_dict["upsert_user"]["inputSchema"]["properties"]
        assert "query" in tool_dict["upsert_user"]["inputSchema"]["properties"]
        assert "header" in tool_dict["upsert_user"]["inputSchema"]["properties"]

        get_user_resp = loop.run_until_complete(
            _async_request(
                starlette_mcp_demo.mcp,
                "tools/call",
                {"name": "get_user", "arguments": {"path": {"uid": 1}}},
            )
        )
        assert get_user_resp["isError"] is False
        assert json.loads(get_user_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

        upsert_resp = loop.run_until_complete(
            _async_request(
                starlette_mcp_demo.mcp,
                "tools/call",
                {
                    "name": "upsert_user",
                    "arguments": {
                        "body": {"name": "so1n", "age": 18},
                        "query": {"notify": True},
                        "header": {"X-Request-Id": "req-1"},
                    },
                },
            )
        )
        assert upsert_resp["isError"] is False
        assert json.loads(upsert_resp["content"][0]["text"]) == {
            "user": {"name": "so1n", "age": 18},
            "notify": True,
            "request_id": "req-1",
        }

        http_resp = loop.run_until_complete(
            _async_request(starlette_mcp_demo.mcp, "tools/call", {"name": "get_http_status", "arguments": {}})
        )
        assert http_resp["isError"] is False
        assert json.loads(http_resp["content"][0]["text"]) == {"mcp": True, "call_mode": "http"}

        resource_resp = loop.run_until_complete(
            _async_request(starlette_mcp_demo.mcp, "resources/read", {"uri": "config://app"})
        )
        assert json.loads(resource_resp["contents"][0]["text"]) == {
            "name": "starlette-mcp-demo",
            "version": "1.0.0",
        }


def test_flask_mcp_doc_example() -> None:
    from docs_source_code.mcp import flask_mcp_demo

    tool_list = _sync_request(flask_mcp_demo.mcp, "tools/list")
    tool_dict = {tool["name"]: tool for tool in tool_list["tools"]}

    assert set(tool_dict) == {"get_user", "upsert_user"}
    assert tool_dict["get_user"]["annotations"] == {"readOnlyHint": True}

    get_user_resp = _sync_request(
        flask_mcp_demo.mcp,
        "tools/call",
        {"name": "get_user", "arguments": {"path": {"uid": 1}}},
    )
    assert get_user_resp["isError"] is False
    assert json.loads(get_user_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    resource_resp = _sync_request(flask_mcp_demo.mcp, "resources/read", {"uri": "config://app"})
    assert json.loads(resource_resp["contents"][0]["text"]) == {
        "name": "flask-mcp-demo",
        "version": "1.0.0",
    }


def test_sanic_mcp_doc_example() -> None:
    from docs_source_code.mcp import sanic_mcp_demo

    with fixture_loop(mock_close_loop=True) as loop:
        tool_list = loop.run_until_complete(_async_request(sanic_mcp_demo.mcp, "tools/list"))
        tool_dict = {tool["name"]: tool for tool in tool_list["tools"]}

        assert set(tool_dict) == {"get_user", "upsert_user", "get_http_status"}
        assert "private_user" not in tool_dict
        assert tool_dict["get_user"]["annotations"] == {"readOnlyHint": True}

        get_user_resp = loop.run_until_complete(
            _async_request(
                sanic_mcp_demo.mcp,
                "tools/call",
                {"name": "get_user", "arguments": {"path": {"uid": 1}}},
            )
        )
        assert get_user_resp["isError"] is False
        assert json.loads(get_user_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

        upsert_resp = loop.run_until_complete(
            _async_request(
                sanic_mcp_demo.mcp,
                "tools/call",
                {
                    "name": "upsert_user",
                    "arguments": {
                        "body": {"name": "so1n", "age": 18},
                        "query": {"notify": True},
                        "header": {"X-Request-Id": "req-1"},
                    },
                },
            )
        )
        assert upsert_resp["isError"] is False
        assert json.loads(upsert_resp["content"][0]["text"]) == {
            "user": {"name": "so1n", "age": 18},
            "notify": True,
            "request_id": "req-1",
        }

        http_resp = loop.run_until_complete(
            _async_request(sanic_mcp_demo.mcp, "tools/call", {"name": "get_http_status", "arguments": {}})
        )
        assert http_resp["isError"] is False
        assert json.loads(http_resp["content"][0]["text"]) == {
            "mcp": True,
            "call_mode": "http",
            "path": "/mcp/http-status",
        }

        resource_resp = loop.run_until_complete(
            _async_request(sanic_mcp_demo.mcp, "resources/read", {"uri": "config://app"})
        )
        assert json.loads(resource_resp["contents"][0]["text"]) == {
            "name": "sanic-mcp-demo",
            "version": "1.0.0",
        }


def test_tornado_mcp_doc_example() -> None:
    from docs_source_code.mcp import tornado_mcp_demo

    with fixture_loop(mock_close_loop=True) as loop:
        tool_list = loop.run_until_complete(_async_request(tornado_mcp_demo.mcp, "tools/list"))
        tool_dict = {tool["name"]: tool for tool in tool_list["tools"]}

        assert set(tool_dict) == {"get_user", "upsert_user"}
        assert "private_user" not in tool_dict
        assert tool_dict["get_user"]["annotations"] == {"readOnlyHint": True}

        get_user_resp = loop.run_until_complete(
            _async_request(
                tornado_mcp_demo.mcp,
                "tools/call",
                {"name": "get_user", "arguments": {"path": {"uid": 1}}},
            )
        )
        assert get_user_resp["isError"] is False
        assert json.loads(get_user_resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

        upsert_resp = loop.run_until_complete(
            _async_request(
                tornado_mcp_demo.mcp,
                "tools/call",
                {
                    "name": "upsert_user",
                    "arguments": {
                        "body": {"name": "so1n", "age": 18},
                        "query": {"notify": True},
                        "header": {"X-Request-Id": "req-1"},
                    },
                },
            )
        )
        assert upsert_resp["isError"] is False
        assert json.loads(upsert_resp["content"][0]["text"]) == {
            "user": {"name": "so1n", "age": 18},
            "notify": True,
            "request_id": "req-1",
        }

        resource_resp = loop.run_until_complete(
            _async_request(tornado_mcp_demo.mcp, "resources/read", {"uri": "config://app"})
        )
        assert json.loads(resource_resp["contents"][0]["text"]) == {
            "name": "tornado-mcp-demo",
            "version": "1.0.0",
        }


def test_apply_mcp_config_doc_example() -> None:
    from docs_source_code.mcp.apply_mcp_config_demo import build_apply_func_list

    apply_func_list = build_apply_func_list()

    assert len(apply_func_list) == 1
    assert callable(apply_func_list[0])
