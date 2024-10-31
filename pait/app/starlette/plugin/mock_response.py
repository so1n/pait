from typing import IO, Any

from starlette.background import BackgroundTask
from starlette.responses import FileResponse, Response

from pait.app.starlette.adapter.response import gen_unifiled_response, set_info_to_response
from pait.plugin.mock_response import MockPluginProtocol


class MockPlugin(MockPluginProtocol[Response]):
    def get_response(self) -> Response:
        return gen_unifiled_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            response_model_class=self.pait_response_model,
        )

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> Response:
        f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        f.seek(0)

        def close_file() -> None:
            temporary_file.__exit__(None, None, None)

        return FileResponse(
            f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
        )

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> Response:
        await f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        await f.seek(0)

        async def close_file() -> None:
            await temporary_file.__aexit__(None, None, None)

        return FileResponse(
            f.name, media_type=self.pait_response_model.media_type, background=BackgroundTask(close_file)
        )

    def set_info_to_response(self, resp: Response) -> None:
        set_info_to_response(resp, self.pait_response_model)
