from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, root_validator

from pait.model.core import PaitCoreModel
from pait.plugin.base import PluginManager, PluginProtocol
from pait.util import get_real_annotation, is_type


class MediaTypeEnum(str, Enum):
    any = ""
    html = "text/html"
    text = "text/plain"
    json = "application/json"


class SimpleRoute(BaseModel):
    methods: List[str]
    route: Callable
    url: str
    media_type_enum: MediaTypeEnum = MediaTypeEnum.any

    @root_validator
    def after_init(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Data association after initializing data"""
        if values["media_type_enum"] is MediaTypeEnum.any:
            route: Callable = values["route"]
            annotations: Dict[str, type] = getattr(route, "__annotations__", None)
            if not annotations:
                raise ValueError(f"Can not found annotation from {route}")
            return_annotations = annotations["return"]
            return_annotations = get_real_annotation(return_annotations, route)
            if return_annotations is not Any:
                if is_type(dict, return_annotations):
                    values["media_type_enum"] = MediaTypeEnum.json
                elif is_type(str, return_annotations):
                    values["media_type_enum"] = MediaTypeEnum.text
                else:
                    raise RuntimeError(f"Unable to parse media type value for routing function:{route}")
        return values


class SimpleRoutePlugin(PluginProtocol):
    status_code: int
    headers: Optional[dict]
    media_type: Optional[str]

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
    pait_core_model.add_plugin([plugin.build(media_type=simple_route.media_type_enum.value)], [])
