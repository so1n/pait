from typing import Any, Type

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin
from pait.util import get_pait_response_model


class CheckJsonRespPlugin(BasePlugin):
    def get_dict_by_resp(self, resp: Any) -> dict:
        raise NotImplementedError()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
            self.pait_core_model.response_model_list, find_core_response_model=True
        )
        response: Any = self.call_next(*args, **kwargs)
        if isinstance(response, dict):
            resp_dict: dict = response
        else:
            resp_dict = self.get_dict_by_resp(response)
        pait_response_model.response_data(**resp_dict)  # type: ignore
        return response


class AsyncCheckJsonRespPlugin(BaseAsyncPlugin):
    def get_dict_by_resp(self, resp: Any) -> dict:
        raise NotImplementedError()

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
            self.pait_core_model.response_model_list, find_core_response_model=True
        )
        response: Any = await self.call_next(*args, **kwargs)
        if isinstance(response, dict):
            resp_dict: dict = response
        else:
            resp_dict = self.get_dict_by_resp(response)
        pait_response_model.response_data(**resp_dict)  # type: ignore
        return response
