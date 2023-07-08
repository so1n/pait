import asyncio
import inspect
from concurrent import futures
from typing import Any, Callable, Optional

__all__ = ["LazyProperty"]


class LazyProperty:
    """Cache field computing resources
    >>> class Demo:
    ...     @LazyProperty()
    ...     def value(self, value):
    ...         return value * value
    """

    def __init__(self, class_: Any = None) -> None:
        self.class_ = class_

    def __call__(self, func: Callable) -> Callable:
        key: str = f"{self.__class__.__name__}_{func.__name__}_future"

        sig = inspect.signature(func)
        if "self" not in sig.parameters and not self.class_:
            raise ValueError("LazyProperty must be used in class method")

        if not asyncio.iscoroutinefunction(func):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                class_ = self.class_ or args[0]
                future: Optional[futures.Future] = getattr(class_, key, None)
                if not future:
                    future = futures.Future()
                    result: Any = func(*args, **kwargs)
                    future.set_result(result)
                    setattr(class_, key, future)
                    return result
                return future.result()

            return wrapper
        else:

            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                class_ = self.class_ or args[0]
                future: Optional[asyncio.Future] = getattr(class_, key, None)
                if not future:
                    future = asyncio.Future()
                    result: Any = await func(*args, **kwargs)
                    future.set_result(result)
                    setattr(class_, key, future)
                    return result
                return future.result()

            return async_wrapper
