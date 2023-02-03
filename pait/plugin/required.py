from typing import Any, Dict, List

from pait.exceptions import CheckValueError
from pait.plugin.base import PluginContext, PluginManager, PostPluginProtocol
from pait.util import gen_tip_exc

__all__ = ["RequiredPlugin", "AsyncRequiredPlugin"]


class RequiredPlugin(PostPluginProtocol):
    """
    Check dependencies between parameters
    """

    required_dict: Dict[str, List[str]]

    def check_param(self, context: PluginContext) -> None:
        try:
            for pre_param, param_list in self.required_dict.items():
                if pre_param not in context.kwargs or not context.kwargs[pre_param]:
                    continue
                for param in param_list:
                    if context.kwargs.get(param, None) is None:
                        raise CheckValueError(
                            f"{pre_param} requires param {' and '.join(param_list)}, which if not none"
                        )
        except Exception as e:
            raise e from gen_tip_exc(context.pait_core_model.func, e)

    @classmethod
    def build(cls, *, required_dict: Dict[str, List[str]]) -> "PluginManager":  # type: ignore
        return super().build(required_dict=required_dict)

    def __call__(self, context: PluginContext) -> Any:
        self.check_param(context)
        return super().__call__(context)


class AsyncRequiredPlugin(RequiredPlugin):
    """"""
