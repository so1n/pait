import json
from typing import Any, AsyncContextManager, Type

import aiofiles  # type: ignore
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response

from pait.g import config
from pait.model import response
from pait.plugin.base_mock_response import BaseAsyncMockPlugin


class MockPlugin(BaseAsyncMockPlugin):
    def mock_response(self, pait_response: Type[response.PaitBaseResponseModel]) -> Any:
        async def make_mock_response() -> Response:
            if issubclass(pait_response, response.PaitJsonResponseModel):
                resp: Response = JSONResponse(
                    json.loads(pait_response.get_example_value(json_encoder_cls=config.json_encoder))
                )
            elif issubclass(pait_response, response.PaitTextResponseModel):
                resp = PlainTextResponse(pait_response.get_example_value(), media_type=pait_response.media_type)
            elif issubclass(pait_response, response.PaitHtmlResponseModel):
                resp = HTMLResponse(pait_response.get_example_value(), media_type=pait_response.media_type)
            elif issubclass(pait_response, response.PaitFileResponseModel):
                named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
                f: Any = await named_temporary_file.__aenter__()
                await f.write(pait_response.get_example_value())
                await f.seek(0)

                async def close_file() -> None:
                    await named_temporary_file.__aexit__(None, None, None)

                resp = FileResponse(f.name, media_type=pait_response.media_type, background=BackgroundTask(close_file))
            else:
                raise NotImplementedError(f"make_mock_response not support {pait_response}")
            resp.status_code = pait_response.status_code[0]
            if pait_response.header:
                resp.headers.update(pait_response.header)
            return resp

        return make_mock_response()
