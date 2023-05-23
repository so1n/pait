import sys
from typing import IO, Any

from flask import Response, send_from_directory

from pait.app.flask.adapter.response import gen_response, set_info_to_response
from pait.plugin.mock_response import MockPluginProtocol

__all__ = ["MockPlugin"]


class MockPlugin(MockPluginProtocol[Response]):
    def get_response(self) -> Response:
        return gen_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            self.pait_response_model,
        )

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> Response:
        try:
            f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
            f.seek(0)
            _, f_path, f_filename = temporary_file.name.split("/")
            return send_from_directory("/" + f_path, f_filename, mimetype=self.pait_response_model.media_type)
        finally:
            exc_type, exc_val, exc_tb = sys.exc_info()
            if exc_type is None:
                temporary_file.__exit__(None, None, None)

    def set_info_to_response(self, resp: Response) -> None:
        set_info_to_response(resp, self.pait_response_model)
