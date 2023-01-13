from typing import Any

import aiofiles  # type: ignore
from tornado.web import RequestHandler

from pait.plugin.base_mock_response import MockPluginProtocol


class MockPlugin(MockPluginProtocol[None]):
    tornado_handle: RequestHandler

    def get_json_response(self) -> None:
        self.tornado_handle.write(self.pait_response_model.get_example_value())

    def get_html_response(self) -> None:
        self.tornado_handle.write(self.pait_response_model.get_example_value())

    def get_text_response(self) -> None:
        self.tornado_handle.write(self.pait_response_model.get_example_value())

    def set_info_to_response(self, resp: None) -> None:
        self.tornado_handle.set_status(self.pait_response_model.status_code[0])
        for key, value in self.pait_response_model.get_header_example_dict().items():
            self.tornado_handle.set_header(key, value)
        self.tornado_handle.set_header("Content-Type", self.pait_response_model.media_type)

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> None:
        await f.write(self.pait_response_model.get_example_value())
        await f.seek(0)
        async for line in f:
            self.tornado_handle.write(line)
        await temporary_file.__aexit__(None, None, None)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.tornado_handle = args[0]
        await super().__call__(args, kwargs)


class AsyncMockPlugin(MockPlugin):
    """"""
