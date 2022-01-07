import json
from typing import Any, Type

from tornado.web import RequestHandler

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import BaseAsyncPlugin
from pait.util import get_pait_response_model


class CheckJsonRespPlugin(BaseAsyncPlugin):
    def get_dict_by_resp(self, resp: Any) -> dict:
        raise NotImplementedError()

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        handler: RequestHandler = args[0]
        pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
            self.pait_core_model.response_model_list, find_core_response_model=True
        )
        response: Any = await self.call_next(*args, **kwargs)
        if not handler._headers["Content-Type"] == "application/json; charset=UTF-8":
            raise TypeError(
                f"{self.__class__.__name__} not support. Content type must `application/json; charset=UTF-8`"
            )
        if len(handler._write_buffer) != 1:
            raise ValueError(f"{self.__class__.__name__} not support, check write buffer length != 1")
        pait_response_model.response_data(**json.loads(handler._write_buffer[0]))  # type: ignore
        return response
