from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

import pydantic

from pait.model.response import PaitBaseResponseModel, PaitJsonResponseModel
from pait.plugin.base import PluginProtocol
from pait.types import is_typeddict
from pait.util import gen_example_dict_from_pydantic_base_model, get_pait_response_model, get_real_annotation

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class CheckJsonRespPlugin(PluginProtocol):
    check_resp_fn: Callable

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if "check_resp_fn" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        pait_response_model: Type[PaitBaseResponseModel] = get_pait_response_model(
            pait_core_model.response_model_list, find_core_response_model=True
        )
        if not issubclass(pait_response_model, PaitJsonResponseModel):
            raise ValueError(f"pait_response_model must {PaitJsonResponseModel} not {pait_response_model}")

        return_type: Optional[Type] = pait_core_model.func.__annotations__.get("return", None)  # type: ignore
        if not return_type:
            raise ValueError(f"Can not found return type by func:{pait_core_model.func}")
        return_type = get_real_annotation(return_type, pait_core_model.func)

        if is_typeddict(return_type):
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

    def _sync_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = self.call_next(*args, **kwargs)
        self.check_resp_fn(response)
        return response

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await self.call_next(*args, **kwargs)
        self.check_resp_fn(response)
        return response

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._is_async_func:
            return self._async_call(*args, **kwargs)
        else:
            return self._sync_call(*args, **kwargs)


class AsyncCheckJsonRespPlugin(CheckJsonRespPlugin):
    """"""
