from dataclasses import MISSING
from typing import Any

from starlette.applications import Starlette


def set_app_attribute(app: Starlette, key: str, value: Any) -> None:
    setattr(app.state, key, value)


def get_app_attribute(app: Any, key: str, default_value: Any = MISSING) -> Any:
    value: Any = getattr(app.state, key, default_value)
    if value is MISSING:
        raise KeyError(f"{key} not found")
    return value
