import inspect
from typing import Any, Callable, Dict, Optional

from any_api.openapi import SecurityModelType


class BaseSecurity:
    model: SecurityModelType
    security_name: str

    def pait_handler(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def set_pait_handler(self, func: Callable) -> None:
        if hasattr(func, "pait_handler"):
            raise ValueError("'func' already has pait_handler")  # pragma: no cover
        class_func: Optional[Callable] = getattr(self, "__call__", None)
        if not class_func:
            raise ValueError("class has no __call__")  # pragma: no cover

        func_sig = inspect.signature(func)
        class_func_sig = inspect.signature(class_func)
        for k, v in func_sig.parameters.items():
            if v.annotation != class_func_sig.parameters[k].annotation:
                raise ValueError(f"func parameter {k} annotation not match")  # pragma: no cover
        if func_sig.return_annotation != class_func_sig.return_annotation:
            raise ValueError("func return annotation not match")

        setattr(self, "pait_handler", func)

    @classmethod
    def get_exception(cls, *, status_code: int, message: str, headers: Optional[Dict] = None) -> Exception:
        return NotImplementedError()  # pragma: no cover
