import sys
from typing import IO, Any

from flask import Response, jsonify, make_response, send_from_directory

from pait.plugin.base_mock_response import MockPluginProtocol

__all__ = ["MockPlugin"]


class MockPlugin(MockPluginProtocol[Response]):
    def _set_str_response(self) -> Response:
        resp: Response = make_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name)
        )
        resp.mimetype = self.pait_response_model.media_type
        return resp

    def get_json_response(self) -> Response:
        return jsonify(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))

    def get_html_response(self) -> Response:
        return self._set_str_response()

    def get_text_response(self) -> Response:
        return self._set_str_response()

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> Response:
        try:
            f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
            f.seek(0)
            _, f_path, f_filename = temporary_file.name.split("/")
            return send_from_directory("/" + f_path, f_filename, mimetype=self.pait_response_model.media_type)
        finally:
            exc_type, exc_val, exc_tb = sys.exc_info()
            temporary_file.__exit__(exc_type, exc_val, exc_tb)

    def set_info_to_response(self, resp: Response) -> None:
        resp.status_code = self.pait_response_model.status_code[0]
        if self.pait_response_model.header:
            resp.headers.update(self.pait_response_model.get_header_example_dict())
