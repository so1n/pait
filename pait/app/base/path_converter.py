import re
from dataclasses import dataclass
from typing import Callable, List, Match, Pattern, Union

Replace = Union[str, Callable[[Match[str]], str]]
OpenAPIReplace = Callable[[str], str]


@dataclass(frozen=True)
class PathRule(object):
    pattern: Pattern[str]
    replace: Replace


class PathConverter(object):
    _openapi_path_param_pattern: Pattern[str] = re.compile(r"{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)(?::[^{}]+)?}")

    def __init__(self, framework_to_openapi_rule_list: List[PathRule], openapi_to_framework: OpenAPIReplace):
        self.framework_to_openapi_rule_list = framework_to_openapi_rule_list
        self.openapi_to_framework = openapi_to_framework

    def get_openapi_path(self, path: str) -> str:
        for rule in self.framework_to_openapi_rule_list:
            path = rule.pattern.sub(rule.replace, path)
        if not path.startswith("/"):
            path = "/" + path
        return path

    def replace_openapi_url_to_url(self, url: str) -> str:
        return self._openapi_path_param_pattern.sub(lambda match: self.openapi_to_framework(match.group("name")), url)
