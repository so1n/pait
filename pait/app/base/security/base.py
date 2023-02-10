from typing import Callable, Dict, Optional

from any_api.openapi import SecurityModelType


class BaseSecurity:
    model: SecurityModelType
    security_name: str

    def _override_call_sig(self, func: Callable) -> None:
        # Compatible with the following syntax
        # BaseSecurity()()
        # BaseSecurity().__call__()
        setattr(self, "_override_call_sig", True)
        setattr(self, "__call__", func)

    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        return NotImplementedError()
