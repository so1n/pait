from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.plugin.base import GetPaitResponseModelFuncType, PrePluginProtocol
from pait.util import get_pait_response_model as _get_pait_response_model

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel
    from pait.plugin.base import PluginManager


class CheckJsonRespPlugin(PrePluginProtocol):
    """Check if the json response result is legal"""

    check_resp_fn: Callable[[Any, "PluginContext"], None]

    @staticmethod
    def get_json(response_data: Any, context: "PluginContext") -> dict:
        raise NotImplementedError()

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if "check_resp_fn" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        get_pait_response_model = kwargs.get("get_pait_response_model", None)
        if not get_pait_response_model:
            raise RuntimeError("Can not found get_pait_response_model func")
        pait_response_model: Type[BaseResponseModel] = get_pait_response_model(pait_core_model.response_model_list)
        if not issubclass(pait_response_model, JsonResponseModel):
            raise ValueError(f"pait_response_model must {JsonResponseModel} not {pait_response_model}")

        def check_resp_by_dict(response_data: Any, context: "PluginContext") -> None:
            if not isinstance(response_data, dict):
                response_data = cls.get_json(response_data, context)
            pait_response_model.response_data(**response_data)  # type: ignore

        kwargs["check_resp_fn"] = check_resp_by_dict
        return kwargs

    def _sync_call(self, context: "PluginContext") -> Any:
        response: Any = super().__call__(context)
        self.check_resp_fn(response, context)
        return response

    async def _async_call(self, context: "PluginContext") -> Any:
        response: Any = await super().__call__(context)
        self.check_resp_fn(response, context)
        return response

    def __call__(self, context: "PluginContext") -> Any:
        if self._is_async_func:
            return self._async_call(context)
        else:
            return self._sync_call(context)

    @classmethod
    def build(  # type: ignore
        cls,  # type: ignore
        get_pait_response_model: Optional[GetPaitResponseModelFuncType] = None,  # type: ignore
    ) -> "PluginManager":  # type: ignore
        return super().build(
            get_pait_response_model=get_pait_response_model or _get_pait_response_model,
        )
