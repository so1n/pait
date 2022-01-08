from typing import Any, Dict, List

from pait.exceptions import CheckValueError
from pait.plugin.base import BaseAsyncPlugin, BasePlugin, PluginProtocol
from pait.util import gen_tip_exc

__all__ = ["RequiredPlugin", "AsyncRequiredPlugin"]


class RequiredPluginProtocol(PluginProtocol):
    """
    Check dependencies between parameters
    """

    is_pre_core: bool = False

    def __init__(self, *, required_dict: Dict[str, List[str]]):
        super().__init__()
        self.required_dict: Dict[str, List[str]] = required_dict

    def check_param(self, *args: Any, **kwargs: Any) -> None:
        try:
            for pre_param, param_list in self.required_dict.items():
                if pre_param not in kwargs or not kwargs[pre_param]:
                    continue
                for param in param_list:
                    if kwargs.get(param, None) is None:
                        raise CheckValueError(
                            f"{pre_param} requires param {' and '.join(param_list)}, which if not none"
                        )
        except Exception as e:
            raise e from gen_tip_exc(self.pait_core_model.func, e)


class RequiredPlugin(RequiredPluginProtocol, BasePlugin):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.check_param(*args, **kwargs)
        return self.call_next(*args, **kwargs)


class AsyncRequiredPlugin(RequiredPluginProtocol, BaseAsyncPlugin):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.check_param(*args, **kwargs)
        return await self.call_next(*args, **kwargs)
