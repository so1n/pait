from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

from pait.model.response import PaitBaseResponseModel
from pait.plugin.base import PluginManager, PluginProtocol
from pait.util import get_pait_response_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class MockPluginProtocol(PluginProtocol):
    pait_response_model: Type[PaitBaseResponseModel]

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if "pait_response_model" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        pait_response: Optional[Type[PaitBaseResponseModel]] = None
        enable_mock_response_filter_fn: Optional[Callable] = kwargs.pop("enable_mock_response_filter_fn", None)
        if enable_mock_response_filter_fn and pait_core_model.response_model_list:
            for _pait_response in pait_core_model.response_model_list:
                if enable_mock_response_filter_fn(_pait_response):
                    pait_response = _pait_response
                    break

        if not pait_response:
            pait_response = get_pait_response_model(
                pait_core_model.response_model_list,
                target_pait_response_class=kwargs.pop("target_pait_response_class", False),
                find_core_response_model=kwargs.pop("find_coro_response_model", None),
            )
        kwargs["pait_response_model"] = pait_response
        return kwargs

    def mock_response(self) -> Any:
        raise NotImplementedError()

    @classmethod
    def build(  # type: ignore
        cls,  # type: ignore
        enable_mock_response_filter_fn: Optional[Callable] = None,  # type: ignore
        target_pait_response_class: Optional[Type["PaitBaseResponseModel"]] = None,  # type: ignore
        find_core_response_model: bool = False,  # type: ignore
    ) -> "PluginManager":  # type: ignore
        return super().build(
            enable_mock_response_filter_fn=enable_mock_response_filter_fn,
            target_pait_response_class=target_pait_response_class,
            find_core_response_model=find_core_response_model,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.mock_response()


class BaseMockPlugin(MockPluginProtocol, ABC):
    """"""


class BaseAsyncMockPlugin(MockPluginProtocol, ABC):
    """"""
