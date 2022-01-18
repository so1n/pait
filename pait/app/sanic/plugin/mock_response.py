from typing import Any, AsyncContextManager

import aiofiles  # type: ignore
from sanic import response as sanic_response
from sanic.response import json as resp_json
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.model import response
from pait.plugin.base_mock_response import BaseAsyncMockPlugin


class MockPlugin(BaseAsyncMockPlugin):
    def mock_response(self) -> Any:
        async def make_mock_response() -> sanic_response.BaseHTTPResponse:
            if issubclass(self.pait_response_model, response.PaitJsonResponseModel):
                resp: sanic_response.BaseHTTPResponse = resp_json(self.pait_response_model.get_example_value())
            elif issubclass(self.pait_response_model, response.PaitTextResponseModel) or issubclass(
                self.pait_response_model, response.PaitHtmlResponseModel
            ):
                resp = sanic_response.text(
                    self.pait_response_model.get_example_value(), content_type=self.pait_response_model.media_type
                )
            elif issubclass(self.pait_response_model, response.PaitFileResponseModel):
                named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
                f: Any = await named_temporary_file.__aenter__()
                await f.write(self.pait_response_model.get_example_value())
                await f.seek(0)
                resp = await sanic_response.file_stream(f.name, mime_type=self.pait_response_model.media_type)

                raw_streaming_fn = resp.streaming_fn

                async def _streaming_fn(_response: sanic_response.BaseHTTPResponse) -> None:
                    await raw_streaming_fn(_response)
                    await named_temporary_file.__aexit__(None, None, None)

                resp.streaming_fn = _streaming_fn
            else:
                raise NotImplementedError(f"make_mock_response not support {self.pait_response_model}")
            resp.status = self.pait_response_model.status_code[0]
            if self.pait_response_model.header:
                resp.headers.update(self.pait_response_model.header)
            return resp

        return make_mock_response()
