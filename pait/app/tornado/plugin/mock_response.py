from typing import Any

import aiofiles  # type: ignore
from tornado.web import RequestHandler

from pait.app.tornado.adapter.response import gen_response, set_info_to_response
from pait.model.context import ContextModel as PluginContext
from pait.plugin.mock_response import MockPluginProtocol


class MockPlugin(MockPluginProtocol[None]):
    tornado_handle: RequestHandler

    def get_response(self) -> None:
        return gen_response(
            self.pait_response_model.get_example_value(example_column_name=self.example_column_name),
            self.pait_response_model,
            self.tornado_handle,
        )

    def set_info_to_response(self, resp: None) -> None:
        set_info_to_response(self.tornado_handle, self.pait_response_model)

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> None:
        await f.write(self.pait_response_model.get_example_value(example_column_name=self.example_column_name))
        await f.seek(0)
        async for line in f:
            self.tornado_handle.write(line)
        await temporary_file.__aexit__(None, None, None)

    async def __call__(self, context: PluginContext) -> Any:
        self.tornado_handle = context.args[0]
        await super().__call__(context)
