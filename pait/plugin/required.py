from typing import Any, Dict, List

from pait.exceptions import CheckValueError
from pait.plugin.base import PluginManager, PluginProtocol
from pait.util import gen_tip_exc

__all__ = ["RequiredPlugin", "AsyncRequiredPlugin"]


class RequiredPlugin(PluginProtocol):
    """
    Check dependencies between parameters
    """

    required_dict: Dict[str, List[str]]

    is_pre_core: bool = False

    def check_param(self, **kwargs: Any) -> None:
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

    @classmethod
    def build(cls, *, required_dict: Dict[str, List[str]]) -> "PluginManager":  # type: ignore
        return super().build(required_dict=required_dict)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.check_param(**kwargs)
        return self.call_next(*args, **kwargs)


class AsyncRequiredPlugin(RequiredPlugin):
    """"""
