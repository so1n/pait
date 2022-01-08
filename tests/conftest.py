from contextlib import contextmanager
from typing import Any, Callable, Generator, List, Type, Union

from pait.g import config
from pait.plugin.base import PluginManager
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin

config.init_config(block_http_method_set={"HEAD", "OPTIONS"})


@contextmanager
def enable_mock(
    route_handler: Callable, mock_plugin_class: Type[Union[BaseMockPlugin, BaseAsyncMockPlugin]]
) -> Generator[None, None, None]:
    """Get the list of plugins through the closure mechanism and load the mock response plugin_class"""
    from pait.param_handle import ParamHandlerMixin

    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")
    plugin_manager_list: List["PluginManager"] = []
    for closure in route_handler.__closure__:  # type: ignore
        value: Any = closure.cell_contents
        if isinstance(value, list) and value[0] and isinstance(value[0], PluginManager):
            plugin_manager_list = value

    index: int = -1
    for _index, plugin_manager in enumerate(plugin_manager_list):
        if issubclass(plugin_manager.plugin_class, ParamHandlerMixin):
            index = _index
            break

    plugin_param: "PluginManager" = PluginManager(mock_plugin_class)
    try:
        plugin_manager_list.insert(index, plugin_param)
        yield
    finally:
        plugin_manager_list.remove(plugin_param)
