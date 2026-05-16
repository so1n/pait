from dataclasses import MISSING
from typing import Any, Dict

_app_attribute_dict: Dict[int, Dict[str, Any]] = {}


def set_app_attribute(app: Any, key: str, value: Any) -> None:
    try:
        setattr(app, key, value)
    except Exception:
        _app_attribute_dict.setdefault(id(app), {})[key] = value


def get_app_attribute(app: Any, key: str, default_value: Any = MISSING) -> Any:
    value: Any = getattr(app, key, MISSING)
    if value is MISSING:
        value = _app_attribute_dict.get(id(app), {}).get(key, default_value)
    if value is MISSING:
        raise KeyError(f"{key} not found")
    return value
