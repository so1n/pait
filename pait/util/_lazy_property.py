import asyncio
from concurrent import futures
from typing import Any, Callable, Optional


class _BoundClass(object):
    pass


_bound_class: _BoundClass = _BoundClass()


class LazyProperty:
    """Cache field computing resources
    >>> class Demo:
    ...     @LazyProperty()
    ...     def value(self, value):
    ...         return value * value
    """

    def __call__(self, func: Callable) -> Callable:
        key: str = f"{self.__class__.__name__}_{func.__name__}_future"
        if not asyncio.iscoroutinefunction(func):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if args and args[0].__class__.__name__ in func.__qualname__:
                    class_: Any = args[0]
                else:
                    class_ = _bound_class
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
                if args and args[0].__class__.__name__ in func.__qualname__:
                    class_: Any = args[0]
                else:
                    class_ = _bound_class
                future: Optional[asyncio.Future] = getattr(class_, key, None)
                if not future:
                    future = asyncio.Future()
                    result: Any = await func(*args, **kwargs)
                    future.set_result(result)
                    setattr(class_, key, future)
                    return result
                return future.result()

            return async_wrapper
