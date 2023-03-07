from dataclasses import MISSING
from typing import Any

from flask import Flask


def set_app_attribute(app: Flask, key: str, value: Any) -> None:
    app.config[key] = value


def get_app_attribute(app: Any, key: str, default_value: Any = MISSING) -> Any:
    value: Any = app.config.get(key, default_value)
    if value is MISSING:
        raise KeyError(f"{key} not found")
    return value
