from contextvars import ContextVar, Token
from typing import Any, Dict, Optional

from pait._pydanitc_adapter import PydanticUndefined

TEMPLATE_CONTEXT: ContextVar[Dict[str, Any]] = ContextVar("template_context", default={})

__all__ = ["TemplateContext", "TemplateVar"]


class TemplateContext(object):
    def __init__(self, template_dict: Dict[str, Any]) -> None:
        self._token: Optional[Token] = None
        self._template_dict: Dict[str, Any] = template_dict

    def __enter__(self) -> "TemplateContext":
        self._token = TEMPLATE_CONTEXT.set(self._template_dict)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._token:
            TEMPLATE_CONTEXT.reset(self._token)
            self._token = None


class TemplateVar(object):
    def __init__(self, name: str, default_value: Any = PydanticUndefined) -> None:
        self._name: str = name
        self._default_value: Any = default_value

    def __call__(self) -> Any:
        return self.get_value_from_template_context()

    def get_value_from_template_context(self) -> Any:
        return TEMPLATE_CONTEXT.get().get(self._name, self._default_value)
