from abc import ABC

from typing import Any, Mapping, Optional


class BaseHelper(object):
    RequestType: Optional[Any] = None
    FormType: Optional[Any] = None
    FileType: Optional[Any] = None

    def __init__(self, request: Any):
        self.request: Any = request

    def body(self) -> dict:
        raise NotImplementedError

    def cookie(self) -> str:
        raise NotImplementedError

    def file(self) -> FileType:
        raise NotImplementedError

    def from_(self) -> FormType:
        raise NotImplementedError

    def header(self) -> str:
        raise NotImplementedError

    def path(self) -> dict:
        raise NotImplementedError

    def query(self) -> dict:
        raise NotImplementedError


class BaseAsyncHelper(BaseHelper, ABC):

    def __init__(self, request: Any):
        super().__init__(request)

    async def body(self) -> dict:
        raise NotImplementedError

    async def file(self):
        raise NotImplementedError

    async def from_(self) -> Mapping:
        raise NotImplementedError
