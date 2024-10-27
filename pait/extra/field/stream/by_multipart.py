import asyncio
import logging
from asyncio import Future as AsyncioFuture
from concurrent.futures import Future as cFuture
from queue import Queue
from typing import Any, AsyncGenerator, Callable, Generator, Mapping, Optional, Type

try:
    from multipart import MultipartSegment, PushMultipartParser, parse_options_header
except ImportError:
    from ._multipart import PushMultipartParser, MultipartSegment, parse_options_header

from pait.g import get_ctx

from .util import BaseStream

logger = logging.getLogger(__name__)


def get_boundary(headers: Mapping) -> str:
    content_type = headers.get("content-type")
    real_content_type, boundary_dict = parse_options_header(content_type)
    assert real_content_type == "multipart/form-data"
    return boundary_dict.get("boundary", "")


class Stream(BaseStream):

    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], Generator[bytes, None, None]],
        parser: Type[PushMultipartParser] = PushMultipartParser,
        queue: Type[Queue] = Queue,
    ):
        self._queue = queue()
        self._info: cFuture[Optional[MultipartSegment]] = cFuture()
        self._parser = parser(get_boundary(headers))

        self._stream_gen = self._step(stream)

        # Reclaim the resource after the request is processed
        get_ctx().contextmanager_list.append(self)  # type: ignore
        super().__init__(headers, stream)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._parser.__exit__(exc_type, exc_val, exc_tb)

    def _step(self, stream: Callable[[], Generator[bytes, None, None]]) -> Generator[Optional[bytearray], None, None]:
        for chunk in stream():
            if not chunk:
                return
            for result in self._parser.parse(chunk):
                if isinstance(result, MultipartSegment):
                    self._info.set_result(result)
                else:
                    if not self._info.done():
                        self._info.set_result(None)
                    if result is not None:
                        self._queue.put(result)
                yield None

    def filename(self) -> Optional[str]:
        info = self.info()
        if info:
            return info.filename
        return None

    def info(self) -> MultipartSegment:
        if self._info.done():
            return self._info.result()

        for _ in self._stream_gen:
            if self._info.done():
                return self._info.result()

    def stream(self) -> Generator[bytes, None, None]:
        for _ in self._stream_gen:
            if self._queue.empty():
                continue
            yield self._queue.get()


class AsyncStream(BaseStream):

    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], AsyncGenerator[bytes, None]],
        parser: Type[PushMultipartParser] = PushMultipartParser,
        queue: Type[asyncio.Queue] = asyncio.Queue,
    ):
        self._queue = queue()
        self._info: AsyncioFuture[Optional[MultipartSegment]] = AsyncioFuture()
        self._parser = parser(get_boundary(headers))

        self._stream_gen = self._step(stream)

        # Reclaim the resource after the request is processed
        get_ctx().contextmanager_list.append(self)  # type: ignore
        super().__init__(headers, stream)

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._parser.__exit__(exc_type, exc_val, exc_tb)

    async def _step(
        self, stream: Callable[[], AsyncGenerator[bytes, None]]
    ) -> AsyncGenerator[Optional[bytearray], None]:
        async for chunk in stream():
            if not chunk:
                return
            for result in self._parser.parse(chunk):
                if isinstance(result, MultipartSegment):
                    self._info.set_result(result)
                else:
                    if not self._info.done():
                        self._info.set_result(None)
                    if result is not None:
                        await self._queue.put(result)
                yield None

    async def filename(self) -> Optional[str]:
        info = await self.info()
        if info:
            return info.filename
        return None

    async def info(self) -> MultipartSegment:
        if self._info.done():
            return self._info.result()

        async for _ in self._stream_gen:
            if self._info.done():
                return self._info.result()

    async def stream(self) -> AsyncGenerator[bytes, None]:
        async for _ in self._stream_gen:
            if self._queue.empty():
                continue
            yield await self._queue.get()
