from typing import Any, List

from pait.exceptions import CheckValueError
from pait.plugin.base import PluginContext, PluginManager, PostPluginProtocol
from pait.util import gen_tip_exc

__all__ = ["AsyncAtMostOneOfPlugin", "AtMostOneOfPlugin"]


class AtMostOneOfPlugin(PostPluginProtocol):
    """
    Check whether each group of parameters appear at the same time
    """

    at_most_one_of_list: List[List[str]]

    def check_param(self, context: PluginContext) -> None:
        try:
            for at_most_one_of in self.at_most_one_of_list:
                if len([i for i in at_most_one_of if context.kwargs.get(i, None) is not None]) > 1:
                    raise CheckValueError(f"requires at most one of param {' or '.join(at_most_one_of)}")
        except Exception as e:
            raise e from gen_tip_exc(context.pait_core_model.func, e)

    @classmethod
    def build(cls, *, at_most_one_of_list: List[List[str]]) -> "PluginManager":  # type: ignore
        return super().build(at_most_one_of_list=at_most_one_of_list)

    def __call__(self, context: PluginContext) -> Any:
        self.check_param(context)
        return super().__call__(context)


class AsyncAtMostOneOfPlugin(AtMostOneOfPlugin):
    """"""
