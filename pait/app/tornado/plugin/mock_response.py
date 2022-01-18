from typing import Any

import aiofiles  # type: ignore
from tornado.web import RequestHandler

from pait.model import response
from pait.plugin.base_mock_response import BaseAsyncMockPlugin


class MockPlugin(BaseAsyncMockPlugin):
    tornado_handle: RequestHandler

    def mock_response(self) -> Any:
        async def make_mock_response() -> Any:
            self.tornado_handle.set_status(self.pait_response_model.status_code[0])
            for key, value in self.pait_response_model.header.items():
                self.tornado_handle.set_header(key, value)
            self.tornado_handle.set_header("Content-Type", self.pait_response_model.media_type)
            if issubclass(self.pait_response_model, response.PaitJsonResponseModel):
                self.tornado_handle.write(self.pait_response_model.get_example_value())
            elif issubclass(self.pait_response_model, response.PaitTextResponseModel) or issubclass(
                self.pait_response_model, response.PaitHtmlResponseModel
            ):
                self.tornado_handle.write(self.pait_response_model.get_example_value())
            elif issubclass(self.pait_response_model, response.PaitFileResponseModel):
                async with aiofiles.tempfile.NamedTemporaryFile() as f:  # type: ignore
                    await f.write(self.pait_response_model.get_example_value())
                    await f.seek(0)
                    async for line in f:
                        self.tornado_handle.write(line)
            else:
                raise NotImplementedError()

        return make_mock_response()

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.tornado_handle = args[0]
        await super().__call__(args, kwargs)
