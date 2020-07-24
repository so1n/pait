import asyncio
from concurrent import futures

from typing import Callable, Optional


class LazyProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = 'cached' + func.__name__

    def __get__(self, obj: object, cls: object):
        if obj is None:
            return self

        if not hasattr(obj, '__dict__'):
            raise AttributeError(f"{cls.__name__} object has no attribute '__dict__'")

        future: Optional['futures.Future'] = getattr(obj, self.cached_name, None)

        def execute_future():
            try:
                res = self.func(obj)
                future.set_result(res)
                return res
            except Exception as e:
                future.set_exception(e)
                raise e

        if future:
            return lambda: future.result()
        else:
            future = futures.Future()
            setattr(obj, self.cached_name, future)
            return lambda: execute_future()


class LazyAsyncProperty:
    def __init__(self, func: Callable):
        self.func: Callable = func
        self.cached_name: str = 'cached_' + func.__name__

    def __get__(self, obj: object, cls: object):
        if obj is None:
            return self

        if not hasattr(obj, '__dict__'):
            raise AttributeError(f"{cls.__name__} object has no attribute '__dict__'")

        future: Optional['asyncio.Future'] = getattr(obj, self.cached_name, None)

        async def await_future():
            return await future

        async def execute_future():
            try:
                res = await self.func(obj)
                future.set_result(res)
                return res
            except Exception as e:
                future.set_exception(e)
                raise e

        if future:
            return await_future
        else:
            future = asyncio.Future()
            setattr(obj, self.cached_name, future)
            return execute_future
