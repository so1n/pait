from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generator, List, Type, Union

from pait.g import config
from pait.model.config import apply_block_http_method_set
from pait.plugin.base import PluginManager
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

config.init_config(
    apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"}, match_key="all", match_value=None)]
)


@contextmanager
def enable_mock(
    route_handler: Callable, mock_plugin_class: Type[Union[BaseMockPlugin, BaseAsyncMockPlugin]]
) -> Generator[None, None, None]:

    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")

    pait_core_model: "PaitCoreModel" = getattr(route_handler, "pait_core_model")
    raw_plugin_manager_list: List["PluginManager"] = pait_core_model._plugin_manager_list
    try:
        pait_core_model.add_plugin([PluginManager(mock_plugin_class)], [])
        yield
    finally:
        pait_core_model._plugin_manager_list = raw_plugin_manager_list