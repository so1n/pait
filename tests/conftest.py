from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generator, List, Type, Union

from pait.g import config
from pait.plugin.base import PluginInitProtocol
from pait.plugin.base_mock_response import BaseAsyncMockPlugin, BaseMockPlugin

if TYPE_CHECKING:
    from pait.core import PluginParamType

config.init_config(block_http_method_set={"HEAD", "OPTIONS"})


@contextmanager
def enable_mock(
    route_handler: Callable, mock_plugin_class: Type[Union[BaseMockPlugin, BaseAsyncMockPlugin]]
) -> Generator[None, None, None]:
    """Get the list of plugins through the closure mechanism and load the mock response plugin"""
    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")
    plugin_list: List["PluginParamType"] = []
    for closure in route_handler.__closure__:  # type: ignore
        value: Any = closure.cell_contents
        if (
            isinstance(value, list)
            and value[0]
            and isinstance(value[0], tuple)
            and issubclass(value[0][0], PluginInitProtocol)
        ):
            plugin_list = value
    plugin_param: "PluginParamType" = (mock_plugin_class, (), {})
    try:
        plugin_list.insert(-1, plugin_param)
        yield
    finally:
        plugin_list.remove(plugin_param)
