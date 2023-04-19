from typing import TYPE_CHECKING, Any, Callable, Dict, Type

from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.plugin.base import PluginContext, PrePluginProtocol
from pait.util import get_pait_response_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class CheckJsonRespPlugin(PrePluginProtocol):
    """Check if the json response result is legal"""

    check_resp_fn: Callable[[Any, PluginContext], None]

    @staticmethod
    def get_json(response_data: Any, context: PluginContext) -> dict:
        raise NotImplementedError()

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if "check_resp_fn" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        pait_response_model: Type[BaseResponseModel] = get_pait_response_model(pait_core_model.response_model_list)
        if not issubclass(pait_response_model, JsonResponseModel):
            raise ValueError(f"pait_response_model must {JsonResponseModel} not {pait_response_model}")

        def check_resp_by_dict(response_data: Any, context: PluginContext) -> None:
            if not isinstance(response_data, dict):
                response_data = cls.get_json(response_data, context)
            pait_response_model.response_data(**response_data)  # type: ignore

        kwargs["check_resp_fn"] = check_resp_by_dict
        return kwargs

    def _sync_call(self, context: PluginContext) -> Any:
        response: Any = super().__call__(context)
        self.check_resp_fn(response, context)
        return response

    async def _async_call(self, context: PluginContext) -> Any:
        response: Any = await super().__call__(context)
        self.check_resp_fn(response, context)
        return response

    def __call__(self, context: PluginContext) -> Any:
        if self._is_async_func:
            return self._async_call(context)
        else:
            return self._sync_call(context)
