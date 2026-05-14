from pait.extra.config import MatchRule, apply_mcp_config
from pait.mcp import MCPConfig


def build_apply_func_list() -> list:
    return [
        apply_mcp_config(
            MCPConfig(include=True, read_only=True),
            match_rule=MatchRule(key="group", target="mcp"),
        )
    ]
