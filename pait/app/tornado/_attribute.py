from dataclasses import MISSING
from typing import Any

from tornado.web import Application


def set_app_attribute(app: Application, key: str, value: Any) -> None:
    app.settings[key] = value


def get_app_attribute(app: Application, key: str, default_value: Any = MISSING) -> Any:
    value: Any = app.settings.get(key, default_value)
    if value is MISSING:
        raise KeyError(f"{key} not found")
    return value
