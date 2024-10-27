from typing import Any, AsyncGenerator, Callable, Generator, Mapping, Union


class BaseStream(object):
    def __init__(
        self,
        headers: Mapping,
        stream: Callable[[], Union[AsyncGenerator[bytes, None], Generator[bytes, None, None]]],
        **kwargs: Any,
    ):
        pass

    def set_request_key(self, request_key: str) -> None:
        pass
