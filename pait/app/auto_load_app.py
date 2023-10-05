import sys
from typing import Any, List

app_list: List = ["flask", "starlette", "sanic", "tornado"]


def auto_load_app_class() -> Any:
    """A project using only a web framework, to use `auto_load_app_class`"""
    load_app_list: list = []
    for app in app_list:
        if app not in sys.modules:
            continue
        load_app_list.append(sys.modules[app])
    if not load_app_list:
        raise RuntimeError("Pait can't auto load app class")
    if len(load_app_list)>=2:
        raise RuntimeError(f"Pait unable to make a choice from [{load_app_list}]")
    return load_app_list[0]
