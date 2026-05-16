import re

from pait.app.base.path_converter import PathConverter, PathRule

path_converter = PathConverter(
    [
        PathRule(
            re.compile(r"<(?:[^:<>/]+:)?(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)>"),
            lambda match: "{" + match.group("name") + "}",
        ),
        PathRule(
            re.compile(r"\(\?P<(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)>[^)]+\)"),
            lambda match: "{" + match.group("name") + "}",
        ),
    ],
    lambda name: f"<path:{name}>",
)
