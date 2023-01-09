from typing import Any

from any_api.openapi import SecurityModelType


class BaseSecurity:
    model: SecurityModelType
    security_name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
