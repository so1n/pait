from tempfile import NamedTemporaryFile
from typing import IO, Any, AsyncContextManager

import aiofiles  # type: ignore
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response

from pait.model import response
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin


class MockAsyncPlugin(BaseAsyncMockPlugin):
    def mock_response(self) -> Any:
        async def make_mock_response() -> Response:
            if issubclass(self.pait_response_model, response.PaitJsonResponseModel):
                resp: Response = JSONResponse(self.pait_response_model.get_example_value())
            elif issubclass(self.pait_response_model, response.PaitTextResponseModel):
                resp = PlainTextResponse(
                    self.pait_response_model.get_example_value(), media_type=self.pait_response_model.media_type
                )
            elif issubclass(self.pait_response_model, response.PaitHtmlResponseModel):
                resp = HTMLResponse(
                    self.pait_response_model.get_example_value(), media_type=self.pait_response_model.media_type
                )
            elif issubclass(self.pait_response_model, response.PaitFileResponseModel):
                named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
                f: Any = await named_temporary_file.__aenter__()
                await f.write(self.pait_response_model.get_example_value())
                await f.seek(0)

                async def close_file() -> None:
                    await named_temporary_file.__aexit__(None, None, None)

                resp = FileResponse(
                    f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
                )
            else:
                raise NotImplementedError(f"make_mock_response not support {self.pait_response_model}")
            resp.status_code = self.pait_response_model.status_code[0]
            if self.pait_response_model.header:
                resp.headers.update(self.pait_response_model.header)
            return resp

        return make_mock_response()


class MockPlugin(BaseMockPlugin):
    def mock_response(self) -> Any:
        if issubclass(self.pait_response_model, response.PaitJsonResponseModel):
            resp: Response = JSONResponse(self.pait_response_model.get_example_value())
        elif issubclass(self.pait_response_model, response.PaitTextResponseModel):
            resp = PlainTextResponse(
                self.pait_response_model.get_example_value(), media_type=self.pait_response_model.media_type
            )
        elif issubclass(self.pait_response_model, response.PaitHtmlResponseModel):
            resp = HTMLResponse(
                self.pait_response_model.get_example_value(), media_type=self.pait_response_model.media_type
            )
        elif issubclass(self.pait_response_model, response.PaitFileResponseModel):
            named_temporary_file: IO = NamedTemporaryFile(delete=True)
            f: Any = named_temporary_file.__enter__()
            f.write(self.pait_response_model.get_example_value())
            f.seek(0)

            def close_file() -> None:
                named_temporary_file.__exit__(None, None, None)

            resp = FileResponse(
                f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
            )
        else:
            raise NotImplementedError(f"make_mock_response not support {self.pait_response_model}")
        resp.status_code = self.pait_response_model.status_code[0]
        if self.pait_response_model.header:
            resp.headers.update(self.pait_response_model.header)
        return resp
