import asyncio
import logging
from concurrent.futures import Future as cFuture
from queue import Queue
from typing import Any, AsyncGenerator, Callable, Generator, Generic, Mapping, Optional, Type, TypeVar, Union

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import BaseTarget

from .util import BaseStream as _BaseStream

FutureT = Union[asyncio.Future, cFuture]
QueueT = Union["asyncio.Queue[Optional[bytes]]", "Queue[Optional[bytes]]"]

_QueueT = TypeVar("_QueueT", bound="QueueT")
_T = TypeVar("_T", bound="Union[AsyncGenerator, Generator]")


logger = logging.getLogger(__name__)


class CustomTarget(BaseTarget):
    def __init__(self, start_future: FutureT, buffer_queue: QueueT, *args: Any, **kwargs: Any) -> None:
        self._start_future = start_future
        self._buffer_queue = buffer_queue
        super().__init__(*args, **kwargs)

    def on_start(self) -> None:
        self._start_future.set_result(True)

    def on_data_received(self, chunk: bytes) -> None:
        if not self._start_future.done():
            return
        self._buffer_queue.put_nowait(chunk)

    def on_finish(self) -> None:
        self._buffer_queue.put_nowait(None)


class BaseStream(_BaseStream, Generic[_T, _QueueT]):
    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], _T],
        queue: _QueueT,
        future: FutureT,
        custom_target: Type[CustomTarget] = CustomTarget,
        streaming_form_data_parse: Type[StreamingFormDataParser] = StreamingFormDataParser,
    ):
        self._start_future = future
        self._buffer_queue = queue

        self._target = custom_target(self._start_future, self._buffer_queue)
        self._parser = streaming_form_data_parse(headers=headers)
        self._parser.register("name", self._target)

        self._stream_gen = stream()
        super().__init__(headers, stream)

    def set_request_key(self, request_key: str) -> None:
        if self._start_future.done():
            raise RuntimeError("The file has been parsed and the request key cannot be set")
        self._parser.register(request_key, self._target)


class Stream(BaseStream[Generator[bytes, None, None], "Queue[Optional[bytes]]"]):

    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], Generator[bytes, None, None]],
        custom_target: Type[CustomTarget] = CustomTarget,
        streaming_form_data_parse: Type[StreamingFormDataParser] = StreamingFormDataParser,
        queue: "Type[Queue[Optional[bytes]]]" = Queue,
    ):
        super().__init__(
            headers,
            stream,
            queue(),
            cFuture(),
            custom_target=custom_target,
            streaming_form_data_parse=streaming_form_data_parse,
        )

    def _step_before_start(self) -> None:
        """Parse data until file information (file name, file type) is obtained"""
        for chunk in self._stream_gen:
            self._parser.data_received(chunk)
            if self._start_future.done():
                break

    def _step_after_start(self) -> Generator[bytes, None, None]:
        """Parse the data and return it if it is part of a file"""
        for chunk in self._stream_gen:
            self._parser.data_received(chunk)

            if not self._buffer_queue.empty():
                real_chunk = self._buffer_queue.get()
                if real_chunk is not None:
                    yield real_chunk
                else:
                    return

    def filename(self) -> Optional[str]:
        if not self._start_future.done():
            self._step_before_start()
        return self._target.multipart_filename

    def stream(self) -> Generator[bytes, None, None]:
        for chunk in self._step_after_start():
            yield chunk


class AsyncStream(BaseStream[AsyncGenerator[bytes, None], "asyncio.Queue[Optional[bytes]]"]):

    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], AsyncGenerator[bytes, None]],
        custom_target: Type[CustomTarget] = CustomTarget,
        streaming_form_data_parse: Type[StreamingFormDataParser] = StreamingFormDataParser,
        queue: "Type[asyncio.Queue[Optional[bytes]]]" = asyncio.Queue,
    ):
        super().__init__(
            headers,
            stream,
            queue(),
            asyncio.Future(),
            custom_target=custom_target,
            streaming_form_data_parse=streaming_form_data_parse,
        )

    async def _step_before_start(self) -> None:
        """Parse data until file information (file name, file type) is obtained"""
        async for chunk in self._stream_gen:
            self._parser.data_received(chunk)
            if self._start_future.done():
                break

    async def _step_after_start(self) -> AsyncGenerator[bytes, None]:
        """Parse the data and return it if it is part of a file"""
        async for chunk in self._stream_gen:
            self._parser.data_received(chunk)

            if not self._buffer_queue.empty():
                real_chunk = await self._buffer_queue.get()
                if real_chunk is not None:
                    yield real_chunk
                else:
                    return

    async def filename(self) -> Optional[str]:
        if not self._start_future.done():
            await self._step_before_start()
        return self._target.multipart_filename

    async def stream(self) -> AsyncGenerator[bytes, None]:
        async for chunk in self._step_after_start():
            yield chunk
