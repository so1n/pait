from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

from pait.model.core import PaitCoreModel
from pait.model.response import BaseResponseModel
from pait.plugin.base import PluginManager, PluginProtocol
from pait.util import get_pait_response_model


class MediaTypeEnum(str, Enum):
    any = ""
    html = "text/html"
    text = "text/plain"
    json = "application/json"


class SimpleRoute(BaseModel):
    methods: List[str]
    route: Callable
    url: str


class SimpleRoutePlugin(PluginProtocol):
    status_code: int
    headers: Optional[dict]
    media_type: Optional[str]

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        if not kwargs["media_type"]:
            if pait_core_model.response_model_list:
                pait_response: Type[BaseResponseModel] = get_pait_response_model(
                    pait_core_model.response_model_list,
                    target_pait_response_class=kwargs.pop("target_pait_response_class", False),
                    find_core_response_model=kwargs.pop("find_coro_response_model", None),
                )
                kwargs["media_type"] = pait_response.media_type
            else:
                raise ValueError(
                    f"The response model list cannot be empty, please add a response model to {pait_core_model.func}"
                )

        return kwargs

    def _merge(self, return_value: Any, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def _call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = super(SimpleRoutePlugin, self).__call__(*args, **kwargs)
        return self._merge(response, *args, **kwargs)

    async def _async_call(self, *args: Any, **kwargs: Any) -> Any:
        response: Any = await super(SimpleRoutePlugin, self).__call__(*args, **kwargs)
        return self._merge(response, *args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._is_async_func:
            return self._async_call(*args, **kwargs)
        else:
            return self._call(*args, **kwargs)

    @classmethod
    def build(  # type: ignore
        cls,
        status_code: Optional[int] = None,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        **kwargs: Any,
    ) -> "PluginManager":
        return super().build(
            status_code=status_code or 200,
            headers=headers or {},
            media_type=media_type,
            **kwargs,
        )


def add_route_plugin(simple_route: SimpleRoute, plugin: Type[SimpleRoutePlugin]) -> None:
    pait_core_model: Optional["PaitCoreModel"] = getattr(simple_route.route, "pait_core_model", None)
    if not pait_core_model:
        raise RuntimeError(f"{simple_route.route} must be a routing function decorated with pait")
    pait_core_model.add_plugin([plugin.build()], [])
