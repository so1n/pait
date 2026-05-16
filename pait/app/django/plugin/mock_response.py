from typing import IO, Any

from django.http import HttpResponse

from pait.app.django.adapter.response import gen_unifiled_response, set_info_to_response
from pait.plugin.mock_response import MockPluginProtocol

__all__ = ["MockPlugin"]


class MockPlugin(MockPluginProtocol[HttpResponse]):
    def get_response(self) -> HttpResponse:
        return gen_unifiled_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            response_model_class=self.pait_response_model,
        )

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> HttpResponse:
        response = HttpResponse(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name)
        )
        response.headers["Content-Type"] = self.pait_response_model.media_type
        return response

    def set_info_to_response(self, resp: HttpResponse) -> None:
        set_info_to_response(resp, self.pait_response_model)
