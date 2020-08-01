import inspect
import logging
from abc import ABC

from typing import Any, Callable, Mapping, Optional, Tuple, Type


class BaseWebDispatch(object):
    RequestType: Optional[Any] = None
    FormType: Optional[Any] = None
    FileType: Optional[Any] = None

    def __init__(
        self,
        func: Callable,
        qualname: str,
        args: Tuple[Any, ...],
        kwargs: Mapping[str, Any]
    ):
        self.cbv_class: Optional[Type] = None
        class_ = getattr(inspect.getmodule(func), qualname)

        request = None
        new_args = []
        for param in args:
            if type(param) == self.RequestType:
                request = param
                # in cbv, request parameter will only appear after the self parameter
                break
            elif isinstance(param, class_):
                self.cbv_class = param
            else:
                # in cbv, parameter like self, request, {other param}
                # not support other param
                logging.warning('Pait only support self and request args param')
                break
            new_args.append(param)

        self.request = request
        self.request_args = new_args
        self.request_kwargs = kwargs

    def body(self) -> dict:
        raise NotImplementedError

    def cookie(self) -> dict:
        raise NotImplementedError

    def file(self) -> FileType:
        raise NotImplementedError

    def form(self) -> FormType:
        raise NotImplementedError

    def header(self) -> dict:
        raise NotImplementedError

    def path(self) -> dict:
        raise NotImplementedError

    def query(self) -> dict:
        raise NotImplementedError


class BaseAsyncWebDispatch(BaseWebDispatch, ABC):

    async def body(self) -> dict:
        raise NotImplementedError

    async def file(self):
        raise NotImplementedError

    async def form(self) -> Mapping:
        raise NotImplementedError
