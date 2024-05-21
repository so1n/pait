from dataclasses import MISSING
from typing import Any

from sanic import Sanic


def set_app_attribute(app: Sanic, key: str, value: Any) -> None:
    setattr(app.ctx, key, value)


def get_app_attribute(app: Sanic, key: str, default_value: Any = MISSING) -> Any:
    value: Any = getattr(app.ctx, key, default_value)
    if value is MISSING:
        raise KeyError(f"{key} not found")
    return value
