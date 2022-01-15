from typing import Any

from tornado.web import RequestHandler

from pait.model.response import PaitJsonResponseModel
from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin as _AsyncAutoCompleteJsonRespPlugin

__all__ = ["AsyncAutoCompleteJsonRespPlugin"]


class AsyncAutoCompleteJsonRespPlugin(_AsyncAutoCompleteJsonRespPlugin):
    def __init__(
        self,
        *,
        pait_response_model: PaitJsonResponseModel,
    ) -> None:
        super(AsyncAutoCompleteJsonRespPlugin, self).__init__(pait_response_model=pait_response_model)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        default_response_dict: dict = self.pait_response_model.get_default_dict()
        response_dict: dict = await self.call_next(*args, **kwargs)
        default_response_dict.update(response_dict)
        tornado_handle: RequestHandler = args[0]
        tornado_handle.write(response_dict)
        return response_dict
