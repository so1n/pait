from typing import Callable, Dict, Optional

from any_api.openapi import SecurityModelType


class BaseSecurity:
    model: SecurityModelType
    security_name: str

    def set_pait_handler(self, func: Callable) -> None:
        if hasattr(func, "pait_handler"):
            raise ValueError("'func' already has pait_handler")  # pragma: no cover
        setattr(self, "pait_handler", func)

    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        return NotImplementedError()  # pragma: no cover
