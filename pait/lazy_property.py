import asyncio
from concurrent import futures
from typing import Any, Callable, Optional, Type


class LazyProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = "cached" + func.__name__

    def __get__(self, obj: object, cls: Type[object]) -> Any:
        if obj is None:
            return self

        if not hasattr(obj, "__dict__"):
            raise AttributeError(f"{cls.__name__} object has no attribute '__dict__'")

        future: Optional["futures.Future"] = getattr(obj, self.cached_name, None)

        if future:
            return lambda: future.result()
        else:
            future = futures.Future()
            setattr(obj, self.cached_name, future)
            try:
                res: Any = self.func(obj)
                future.set_result(res)
                return res
            except Exception as e:
                future.set_exception(e)
                raise e


class LazyAsyncProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = "cached_" + func.__name__

    def __get__(self, obj: object, cls: Type[object]) -> Any:
        if obj is None:
            return self

        if not hasattr(obj, "__dict__"):
            raise AttributeError(f"{cls.__name__} object has no attribute '__dict__'")

        future: Optional["asyncio.Future"] = getattr(obj, self.cached_name, None)

        if future:
            return future
        else:
            future = asyncio.Future()
            setattr(obj, self.cached_name, future)
            return self._execute_future(future, obj)

    async def _execute_future(self, future: asyncio.Future, obj: object) -> Any:
        try:
            res = await self.func(obj)
            future.set_result(res)
            return res
        except Exception as e:
            future.set_exception(e)
            raise e
