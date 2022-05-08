from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generator, List

from pait.extra.config import apply_block_http_method_set
from pait.g import config
from pait.plugin.base import PluginManager

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])


@contextmanager
def enable_plugin(route_handler: Callable, *plugin_manager_list: PluginManager) -> Generator[None, None, None]:
    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")

    pait_core_model: "PaitCoreModel" = getattr(route_handler, "pait_core_model")
    raw_plugin_manager_list: List["PluginManager"] = pait_core_model._plugin_manager_list

    plugin_list: List[PluginManager] = []
    post_plugin_list: List[PluginManager] = []
    for plugin_manager in plugin_manager_list:
        if plugin_manager.plugin_class.is_pre_core:
            plugin_list.append(plugin_manager)
        else:
            post_plugin_list.append(plugin_manager)
    try:
        pait_core_model.add_plugin(plugin_list, post_plugin_list)
        yield
    finally:
        pait_core_model._plugin_manager_list = raw_plugin_manager_list
