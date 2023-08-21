import copy
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from pait.model.response import BaseResponseModel, JsonResponseModel
from pait.plugin.base import GetPaitResponseModelFuncType, PrePluginProtocol
from pait.util import get_pait_response_model as _get_pait_response_model

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel
    from pait.plugin.base import PluginManager


class AutoCompleteJsonRespPlugin(PrePluginProtocol):
    default_response_dict: dict

    def _merge(self, source_dict: dict, target_dict: dict) -> None:
        for key, value in source_dict.items():
            if isinstance(value, dict) and key in target_dict:
                self._merge(value, target_dict[key])
            elif value and isinstance(value, list) and key in target_dict:
                raw_value = value.pop()
                for item in target_dict[key]:
                    new_value = copy.deepcopy(raw_value)
                    self._merge(new_value, item)
                    value.append(new_value)
            else:
                source_dict[key] = target_dict.get(key, value)

    def merge(self, response_dict: dict) -> dict:
        default_response_dict: dict = copy.deepcopy(self.default_response_dict)
        self._merge(default_response_dict, response_dict)
        return default_response_dict

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if "default_response_dict" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        get_pait_response_model = kwargs.get("get_pait_response_model", None)
        if not get_pait_response_model:
            raise RuntimeError("Can not found get_pait_response_model func")
        pait_response_model: Type[BaseResponseModel] = get_pait_response_model(pait_core_model.response_model_list)
        if not issubclass(pait_response_model, JsonResponseModel):
            raise ValueError(f"pait_response_model must `{JsonResponseModel.__name__}` not {pait_response_model}")
        kwargs["default_response_dict"] = pait_response_model.get_default_dict()
        return kwargs

    def _sync_call(self, context: "PluginContext") -> Any:
        response_dict: dict = super().__call__(context)
        return self.merge(response_dict)

    async def _async_call(self, context: "PluginContext") -> Any:
        response_dict: dict = await super().__call__(context)
        return self.merge(response_dict)

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
