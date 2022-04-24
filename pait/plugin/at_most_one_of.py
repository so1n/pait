from typing import Any, List

from pait.exceptions import CheckValueError
from pait.plugin.base import PluginManager, PluginProtocol
from pait.util import gen_tip_exc

__all__ = ["AsyncAtMostOneOfPlugin", "AtMostOneOfPlugin"]


class AtMostOneOfPlugin(PluginProtocol):
    """
    Check whether each group of parameters appear at the same time
    """

    at_most_one_of_list: List[List[str]]

    is_pre_core: bool = False

    def check_param(self, **kwargs: Any) -> None:
        try:
            for at_most_one_of in self.at_most_one_of_list:
                if len([i for i in at_most_one_of if kwargs.get(i, None) is not None]) > 1:
                    raise CheckValueError(f"requires at most one of param {' or '.join(at_most_one_of)}")
        except Exception as e:
            raise e from gen_tip_exc(self.pait_core_model.func, e)

    @classmethod
    def build(cls, *, at_most_one_of_list: List[List[str]]) -> "PluginManager":  # type: ignore
        return super().build(at_most_one_of_list=at_most_one_of_list)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.check_param(**kwargs)
        return self.call_next(*args, **kwargs)


class AsyncAtMostOneOfPlugin(AtMostOneOfPlugin):
    """"""
