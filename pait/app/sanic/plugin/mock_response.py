from typing import Any

import aiofiles  # type: ignore
from sanic import response as sanic_response
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.sanic.adapter.response import gen_response, set_info_to_response
from pait.plugin.mock_response import MockPluginProtocol


class MockPlugin(MockPluginProtocol[sanic_response.BaseHTTPResponse]):
    def get_response(self) -> sanic_response.BaseHTTPResponse:
        return gen_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            self.pait_response_model,
        )

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> sanic_response.BaseHTTPResponse:
        await f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        await f.seek(0)
        resp = await sanic_response.file_stream(f.name, mime_type=self.pait_response_model.media_type)

        raw_streaming_fn = resp.streaming_fn

        async def _streaming_fn(_response: sanic_response.BaseHTTPResponse) -> None:
            await raw_streaming_fn(_response)
            await temporary_file.__aexit__(None, None, None)

        resp.streaming_fn = _streaming_fn
        return resp

    def set_info_to_response(self, resp: sanic_response.BaseHTTPResponse) -> None:
        set_info_to_response(resp, self.pait_response_model)
