from typing import IO, Any

import aiofiles  # type: ignore
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, Response

from pait.plugin.base_mock_response import RESP_T, MockPluginProtocol


class MockPlugin(MockPluginProtocol[Response]):
    def get_json_response(self) -> Response:
        return JSONResponse(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))

    def get_html_response(self) -> Response:
        return PlainTextResponse(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            media_type=self.pait_response_model.media_type,
        )

    def get_text_response(self) -> Response:
        return PlainTextResponse(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            media_type=self.pait_response_model.media_type,
        )

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> RESP_T:
        f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        f.seek(0)

        def close_file() -> None:
            temporary_file.__exit__(None, None, None)

        return FileResponse(
            f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
        )

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> RESP_T:
        await f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        await f.seek(0)

        async def close_file() -> None:
            await temporary_file.__aexit__(None, None, None)

        return FileResponse(
            f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
        )

    def set_info_to_response(self, resp: Response) -> None:
        resp.status_code = self.pait_response_model.status_code[0]
        if self.pait_response_model.header:
            resp.headers.update(self.pait_response_model.get_header_example_dict())


class AsyncMockPlugin(MockPlugin):
    """"""
