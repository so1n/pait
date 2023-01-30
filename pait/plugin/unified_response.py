from abc import ABCMeta
from typing import Any, Dict, Optional, Type

from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel, FileResponseModel
from pait.plugin.base import PrePluginProtocol
from pait.util import get_pait_response_model


class UnifiedResponsePluginProtocol(PrePluginProtocol):
    response_model_class: Type[BaseResponseModel]

    def _gen_response(self, return_value: Any, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        if pait_core_model.response_model_list:
            pait_response: Type[BaseResponseModel] = get_pait_response_model(
                pait_core_model.response_model_list,
                target_pait_response_class=kwargs.pop("target_pait_response_class", False),
                find_core_response_model=kwargs.pop("find_coro_response_model", None),
            )
            if issubclass(pait_response, FileResponseModel):
                raise ValueError(f"Not Support {FileResponseModel.__name__}")
            kwargs["response_model_class"] = pait_response
        else:
            raise ValueError(
                f"The response model list cannot be empty, please add a response model to {pait_core_model.func}"
            )
        return kwargs


class UnifiedResponsePlugin(UnifiedResponsePluginProtocol, metaclass=ABCMeta):
    status_code: int
    headers: Optional[dict]
    media_type: Optional[str]

    def _call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super(UnifiedResponsePlugin, self).__call__(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(UnifiedResponsePlugin, self).__call__(*args, **kwargs)
        return self._gen_response(response, *args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._is_async_func:
            return self._async_call(*args, **kwargs)
        else:
            return self._call(*args, **kwargs)
