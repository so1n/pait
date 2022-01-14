import json
from tempfile import NamedTemporaryFile

from flask import Response, jsonify, make_response, send_from_directory

from pait.g import config
from pait.model import response
from pait.plugin.base_mock_response import BaseMockPlugin

__all__ = ["MockPlugin"]


class MockPlugin(BaseMockPlugin):
    def mock_response(self) -> Response:
        if issubclass(self.pait_response, response.PaitJsonResponseModel):
            resp: Response = jsonify(
                json.loads(self.pait_response.get_example_value(json_encoder_cls=config.json_encoder))
            )
        elif issubclass(self.pait_response, response.PaitTextResponseModel) or issubclass(
            self.pait_response, response.PaitHtmlResponseModel
        ):
            resp = make_response(self.pait_response.get_example_value())
            resp.mimetype = self.pait_response.media_type
        elif issubclass(self.pait_response, response.PaitFileResponseModel):
            with NamedTemporaryFile(delete=True) as temporary_file:
                temporary_file.write(self.pait_response.get_example_value())
                temporary_file.seek(0)
                _, f_path, f_filename = temporary_file.name.split("/")
                resp = send_from_directory("/" + f_path, f_filename, mimetype=self.pait_response.media_type)
        else:
            raise NotImplementedError(f"make_mock_response not support {self.pait_response}")
        resp.status_code = self.pait_response.status_code[0]
        if self.pait_response.header:
            resp.headers.update(self.pait_response.header)  # type: ignore
        return resp
