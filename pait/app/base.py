import logging
from abc import ABC
from typing import Any, List, Mapping, Optional, Tuple, Type


class BaseAppHelper(object):
    """Provide a unified framework call interface for pait"""

    RequestType = type(None)
    FormType = type(None)
    FileType = type(None)
    HeaderType = type(None)

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        """
        Extract the required data from the passed parameters,
        such as the self parameter in cvb mode, the request parameter in starletter
        """
        self.cbv_class: Optional[Type] = None

        request = None
        new_args: List[Any] = []
        for param in args:
            if type(param) == self.RequestType:
                request = param
                # In cbv, request parameter will only appear after the self parameter
                break
            elif isinstance(param, class_):
                self.cbv_class = param
            else:
                # In cbv, parameter like self, request, {other param}
                # Now, not support other param
                logging.warning("Pait only support self and request args param")
                break
            new_args.append(param)

        self.request: Any = request
        self.request_args: List[Any] = new_args
        self.request_kwargs: Mapping[str, Any] = kwargs

    def body(self) -> dict:
        raise NotImplementedError

    def cookie(self) -> dict:
        raise NotImplementedError

    def file(self) -> FileType:
        raise NotImplementedError

    def form(self) -> FormType:
        raise NotImplementedError

    def header(self) -> HeaderType:
        raise NotImplementedError

    def path(self) -> dict:
        raise NotImplementedError

    def query(self) -> dict:
        raise NotImplementedError


class BaseAsyncAppHelper(BaseAppHelper, ABC):
    async def body(self) -> dict:
        raise NotImplementedError

    async def file(self):
        raise NotImplementedError

    async def form(self) -> Mapping:
        raise NotImplementedError
