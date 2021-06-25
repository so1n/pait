import sys
from typing import Any, List

app_list: List = ["flask", "starlette", "sanic", "tornado"]


def auto_load_app_class() -> Any:
    """A project using only a web framework, to use `auto_load_app_class`"""
    real_app: Any = None
    for app in app_list:
        if app not in sys.modules:
            continue
        if real_app:
            raise RuntimeError(f"Pait unable to make a choice {real_app} & {app}")
        real_app = sys.modules[app]
    if not real_app:
        raise RuntimeError("Pait can't auto load app class")
    return real_app
