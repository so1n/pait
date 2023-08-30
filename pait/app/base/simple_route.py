from typing import Callable, List, Optional, Type

from pydantic import BaseModel, Field

from pait.model.core import PaitCoreModel
from pait.plugin.unified_response import UnifiedResponsePlugin


class SimpleRoute(BaseModel):
    methods: List[str]
    route: Callable
    url: str
    kwargs: dict = Field(default_factory=dict)


def add_route_plugin(simple_route: SimpleRoute, plugin: Type[UnifiedResponsePlugin]) -> None:
    pait_core_model: Optional["PaitCoreModel"] = getattr(simple_route.route, "pait_core_model", None)
    if not pait_core_model:
        raise RuntimeError(f"{simple_route.route} must be a routing function decorated with pait")
    pait_core_model.add_plugin([plugin.build()], [])
