import asyncio
import copy
import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generator, List, Optional, Type

import pytest

from pait.model.context import ContextModel
from pait.model.response import BaseResponseModel
from pait.plugin.base import PluginManager, PrePluginProtocol
from pait.util import ignore_pre_check

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


# Detects if a blocking function is encountered
os.environ["PYTHONASYNCIODEBUG"] = "1"


@pytest.fixture
def pait_context() -> Generator[ContextModel, None, None]:
    from pait.app.base import BaseAppHelper

    class FakePluginCoreModel:
        func = lambda x: x  # noqa

    yield ContextModel(
        cbv_instance=None,
        app_helper=BaseAppHelper,  # type: ignore
        pait_core_model=FakePluginCoreModel(),  # type: ignore
        args=[],
        kwargs={},
    )


@contextmanager
def enable_plugin(
    route_handler: Callable, *plugin_manager_list: PluginManager, is_replace: bool = False
) -> Generator[None, None, None]:
    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")

    pait_core_model: "PaitCoreModel" = getattr(route_handler, "pait_core_model")
    raw_plugin_list: List[PluginManager] = copy.deepcopy(pait_core_model._plugin_list)
    raw_post_plugin_list: List[PluginManager] = copy.deepcopy(pait_core_model._post_plugin_list)

    plugin_list: List[PluginManager] = []
    post_plugin_list: List[PluginManager] = []
    for plugin_manager in plugin_manager_list:
        if issubclass(plugin_manager.plugin_class, PrePluginProtocol):
            plugin_list.append(plugin_manager)
        else:
            post_plugin_list.append(plugin_manager)
    try:
        if is_replace:
            for _plugin in plugin_list + post_plugin_list:
                if not ignore_pre_check:
                    plugin_manager.pre_check_hook(route_handler.pait_core_model)  # type: ignore[attr-defined]
                plugin_manager.pre_load_hook(route_handler.pait_core_model)  # type: ignore[attr-defined]

            pait_core_model._plugin_list = plugin_list
            pait_core_model._post_plugin_list = post_plugin_list
            pait_core_model.build_plugin_stack()
        else:
            pait_core_model.add_plugin(plugin_list, post_plugin_list)
            pait_core_model.build_plugin_stack()
        yield
    finally:
        pait_core_model._plugin_list = raw_plugin_list
        pait_core_model._post_plugin_list = raw_post_plugin_list
        pait_core_model.build_plugin_stack()


@contextmanager
def enable_resp_model(route_handler: Callable, *resp_list: Type[BaseResponseModel]) -> Generator[None, None, None]:
    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")

    pait_core_model: "PaitCoreModel" = getattr(route_handler, "pait_core_model")
    raw_resp_list: List[Type[BaseResponseModel]] = copy.deepcopy(pait_core_model.response_model_list)

    try:
        pait_core_model._response_model_list = resp_list  # type: ignore[assignment]
        yield
    finally:
        pait_core_model._response_model_list = raw_resp_list


@contextmanager
def fixture_loop(mock_close_loop: bool = False) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def _mock(_loop: Optional[asyncio.AbstractEventLoop] = None) -> Optional[asyncio.AbstractEventLoop]:
        return loop

    if mock_close_loop:
        close_loop = loop.close
    set_event_loop = asyncio.set_event_loop
    new_event_loop = asyncio.new_event_loop
    try:
        asyncio.set_event_loop = _mock  # type: ignore
        asyncio.new_event_loop = _mock  # type: ignore
        if mock_close_loop:
            loop.close = lambda: None  # type: ignore
        yield loop
    finally:
        asyncio.set_event_loop = set_event_loop
        asyncio.new_event_loop = new_event_loop
        if mock_close_loop:
            loop.close = close_loop  # type: ignore
    return None
