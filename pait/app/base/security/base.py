from typing import Any, Dict, Optional

from any_api.openapi import SecurityModelType


class BaseSecurity:
    model: SecurityModelType
    security_name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        return NotImplementedError()
