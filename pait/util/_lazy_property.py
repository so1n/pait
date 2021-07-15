import asyncio
from concurrent import futures
from typing import Any, Callable, Optional


class _BoundClass(object):
    pass


_bound_class: _BoundClass = _BoundClass()


class LazyProperty:
    """Cache field computing resources
    >>> class Demo:
    ...     @LazyProperty(is_class_func=True)
    ...     def value(self, value):
    ...         return value * value
    """

    def __init__(self, is_class_func: bool = False):
        self._is_class_func: bool = is_class_func

    def __call__(self, func: Callable) -> Callable:
        key: str = f"{self.__class__.__name__}_{func.__name__}_future"
        if not asyncio.iscoroutinefunction(func):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                class_: Any = args[0] if self._is_class_func else _bound_class
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
                class_: Any = args[0] if self._is_class_func else _bound_class
                future: Optional[asyncio.Future] = getattr(class_, key, None)
                if not future:
                    future = asyncio.Future()
                    result: Any = await func(*args, **kwargs)
                    future.set_result(result)
                    setattr(class_, key, future)
                    return result
                return future.result()

            return async_wrapper
