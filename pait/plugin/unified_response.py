from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel, FileResponseModel
from pait.plugin.base import GetPaitResponseModelFuncType, PluginManager, PrePluginProtocol
from pait.util import get_pait_response_model as _get_pait_response_model

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext


class UnifiedResponsePluginProtocol(PrePluginProtocol):
    response_model_class: Type[BaseResponseModel]

    def _gen_response(self, return_value: Any, context: "PluginContext") -> Any:
        raise NotImplementedError

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        get_pait_response_model = kwargs.get("get_pait_response_model", None)
        if not get_pait_response_model:
            raise RuntimeError("Can not found get_pait_response_model func")
        if pait_core_model.response_model_list:
            pait_response: Type[BaseResponseModel] = get_pait_response_model(pait_core_model.response_model_list)
            if issubclass(pait_response, FileResponseModel):
                raise ValueError(f"Not Support {FileResponseModel.__name__}")
            kwargs["response_model_class"] = pait_response
        else:
            raise ValueError(
                f"The response model list cannot be empty, please add a response model to"
                f" {pait_core_model.func.__qualname__}"
            )
        return kwargs


class UnifiedResponsePlugin(UnifiedResponsePluginProtocol, metaclass=ABCMeta):
    status_code: int
    headers: Optional[dict]
    media_type: Optional[str]

    def __call__(self, context: "PluginContext") -> Any:
        if self._is_async_func:
            return self._async_call(context)
        return self._sync_call(context)

    def _sync_call(self, context: "PluginContext") -> Any:
        response: Any = super(UnifiedResponsePlugin, self).__call__(context)
        return self._gen_response(response, context)

    async def _async_call(self, context: "PluginContext") -> Any:
        response: Any = await super(UnifiedResponsePlugin, self).__call__(context)
        return self._gen_response(response, context)

    @classmethod
    def build(  # type: ignore
        cls,  # type: ignore
        get_pait_response_model: Optional[GetPaitResponseModelFuncType] = None,  # type: ignore
    ) -> "PluginManager":  # type: ignore
        return super().build(
            get_pait_response_model=get_pait_response_model or _get_pait_response_model,
        )
