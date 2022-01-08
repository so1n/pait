import sys
from typing import Any, Callable, Dict, ForwardRef, Optional, Type

import pydantic

from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel, PaitJsonResponseModel
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import get_pait_response_model


class JsonRespPluginProtocolMixin(PluginProtocol):
    def __init__(self, *, check_resp_fn: Callable) -> None:
        super(JsonRespPluginProtocolMixin, self).__init__()
        self.check_resp_fn: Callable = check_resp_fn

    @classmethod
    def cls_hook_by_core_model(cls, pait_core_model: PaitCoreModel, kwargs: Dict) -> Dict:
        super().cls_hook_by_core_model(pait_core_model, kwargs)
        return_type: Optional[Type] = pait_core_model.func.__annotations__.get("return", None)  # type: ignore
        if not return_type:
            raise ValueError(f"Can not found return type by func:{pait_core_model.func}")
        if isinstance(return_type, str):
            value: ForwardRef = ForwardRef(return_type, is_argument=False)
            return_type = value._evaluate(sys.modules[pait_core_model.func.__module__].__dict__, None)  # type: ignore
        try:
            if issubclass(return_type, dict):
                pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
                    pait_core_model.response_model_list, find_core_response_model=True
                )
                if not issubclass(pait_response_model, PaitJsonResponseModel):
                    raise ValueError(
                        f"pait_response_model must {PaitJsonResponseModel} not {kwargs['pait_response_model']}"
                    )

                def check_resp_by_dict(response_dict: dict) -> None:
                    pait_response_model.response_data(**response_dict)  # type: ignore

                kwargs["check_resp_fn"] = check_resp_by_dict
            else:
                raise ValueError(f"Can not found {cls.__name__} support return type")
        except TypeError as e:
            if str(e) == "TypedDict does not support instance and class checks":

                def check_resp_by_typed_dict(response_dict: dict) -> None:
                    pydantic.create_model_from_typeddict(return_type)(**response_dict)  # type: ignore

                kwargs["check_resp_fn"] = check_resp_by_typed_dict
            else:
                raise e
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
