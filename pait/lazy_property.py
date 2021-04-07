import asyncio
from concurrent import futures
from typing import Any, Callable, Optional, Type


class LazyProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = "cached" + func.__name__

    def __get__(self, obj: object, cls: Type[object]) -> Any:
        future: Optional["futures.Future"] = getattr(obj, self.cached_name, None)

        if future:
            return lambda: future.result()
        else:
            future = futures.Future()
            setattr(obj, self.cached_name, future)
            try:
                res: Any = self.func(obj)
                future.set_result(res)
                return lambda: res
            except Exception as e:
                future.set_exception(e)
                raise e


class LazyAsyncProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = "cached_" + func.__name__

    def __get__(self, obj: object, cls: Type[object]) -> Any:
        future: Optional["asyncio.Future"] = getattr(obj, self.cached_name, None)

        if future:
            return lambda: future
        else:
            future = asyncio.Future()
            setattr(obj, self.cached_name, future)
            return lambda: self._execute_future(future, obj)

    async def _execute_future(self, future: asyncio.Future, obj: object) -> Any:
        try:
            res = await self.func(obj)
            future.set_result(res)
        except Exception as e:
            future.set_exception(e)
        return await future
