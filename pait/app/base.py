import logging
from abc import ABC
from typing import Any, List, Mapping, Optional, Tuple, Type
from pait.lazy_property import LazyAsyncProperty, LazyProperty


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

    @LazyProperty
    def cookie(self) -> Any:
        raise NotImplementedError

    @LazyProperty
    def header(self) -> Any:
        raise NotImplementedError

    @LazyProperty
    def path(self) -> Any:
        raise NotImplementedError

    @LazyProperty
    def query(self) -> Any:
        raise NotImplementedError

    def check_request_type(self, value: Any) -> bool:
        return value is self.RequestType

    def check_file_type(self, value: Any) -> bool:
        return value is self.FileType

    def check_form_type(self, value: Any) -> bool:
        return value is self.FormType

    def check_header_type(self, value: Any) -> bool:
        return value is self.HeaderType


class BaseSyncAppHelper(BaseAppHelper, ABC):

    @LazyProperty
    def body(self) -> Any:
        raise NotImplementedError

    @LazyProperty
    def file(self) -> Any:
        raise NotImplementedError

    @LazyProperty
    def form(self) -> Any:
        raise NotImplementedError


class BaseAsyncAppHelper(BaseAppHelper, ABC):

    @LazyAsyncProperty
    async def body(self) -> dict:
        raise NotImplementedError

    @LazyAsyncProperty
    async def file(self) -> Any:
        raise NotImplementedError

    @LazyAsyncProperty
    async def form(self) -> Mapping:
        raise NotImplementedError
