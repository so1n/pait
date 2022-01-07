import json
from typing import Any, AsyncContextManager, Type

import aiofiles  # type: ignore
from sanic import response as sanic_response
from sanic.response import json as resp_json
from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.g import config
from pait.model import response
from pait.plugin.base_mock_response import BaseAsyncMockPlugin


class MockPlugin(BaseAsyncMockPlugin):
    def mock_response(self, pait_response: Type[response.PaitBaseResponseModel]) -> Any:
        async def make_mock_response() -> sanic_response.BaseHTTPResponse:
            if issubclass(pait_response, response.PaitJsonResponseModel):
                resp: sanic_response.BaseHTTPResponse = resp_json(
                    json.loads(pait_response.get_example_value(json_encoder_cls=config.json_encoder))
                )
            elif issubclass(pait_response, response.PaitTextResponseModel) or issubclass(
                pait_response, response.PaitHtmlResponseModel
            ):
                resp = sanic_response.text(pait_response.get_example_value(), content_type=pait_response.media_type)
            elif issubclass(pait_response, response.PaitFileResponseModel):
                named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
                f: Any = await named_temporary_file.__aenter__()
                await f.write(pait_response.get_example_value())
                await f.seek(0)
                resp = await sanic_response.file_stream(f.name, mime_type=pait_response.media_type)

                raw_streaming_fn = resp.streaming_fn

                async def _streaming_fn(_response: sanic_response.BaseHTTPResponse) -> None:
                    await raw_streaming_fn(_response)
                    await named_temporary_file.__aexit__(None, None, None)

                resp.streaming_fn = _streaming_fn
            else:
                raise NotImplementedError(f"make_mock_response not support {pait_response}")
            resp.status = pait_response.status_code[0]
            if pait_response.header:
                resp.headers.update(pait_response.header)
            return resp

        return make_mock_response()
