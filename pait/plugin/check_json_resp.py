from typing import Any, Callable, Dict, Optional, Type

import pydantic

from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel, PaitJsonResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import gen_example_dict_from_pydantic_base_model, get_pait_response_model, get_real_annotation


class JsonRespPluginProtocolMixin(PluginProtocol):
    def __init__(self, *, check_resp_fn: Callable) -> None:
        super(JsonRespPluginProtocolMixin, self).__init__()
        self.check_resp_fn: Callable = check_resp_fn

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: PaitCoreModel, kwargs: Dict) -> Dict:
        kwargs = super().cls_hook_by_core_model(pait_core_model, kwargs)
        if "check_resp_fn" in kwargs:
            raise RuntimeError("Please use response_model_list param")

        pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
            pait_core_model.response_model_list, find_core_response_model=True
        )
        if not issubclass(pait_response_model, PaitJsonResponseModel):
            raise ValueError(f"pait_response_model must {PaitJsonResponseModel} not {pait_response_model}")

        return_type: Optional[Type] = pait_core_model.func.__annotations__.get("return", None)  # type: ignore
        if not return_type:
            raise ValueError(f"Can not found return type by func:{pait_core_model.func}")
        return_type = get_real_annotation(return_type, pait_core_model.func)

        if hasattr(return_type, "__required_keys__"):
            base_model_class: Type[pydantic.BaseModel] = pydantic.create_model_from_typeddict(
                return_type  # type: ignore
            )
            base_model_class(**gen_example_dict_from_pydantic_base_model(pait_response_model.response_data))

        elif not issubclass(return_type, dict):
            raise ValueError(f"Can not found {cls.__name__} support return type")

        def check_resp_by_dict(response_dict: dict) -> None:
            pait_response_model.response_data(**response_dict)  # type: ignore

        kwargs["check_resp_fn"] = check_resp_by_dict
        return kwargs


class CheckJsonRespPlugin(JsonRespPluginProtocolMixin, BasePlugin):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = self.call_next(*args, **kwargs)
        self.check_resp_fn(response)
        return response


class AsyncCheckJsonRespPlugin(JsonRespPluginProtocolMixin, BaseAsyncPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await self.call_next(*args, **kwargs)
        self.check_resp_fn(response)
        return response
