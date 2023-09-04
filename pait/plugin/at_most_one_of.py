from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pait.exceptions import CheckValueError
from pait.field import BaseRequestResourceField, ExtraParam
from pait.plugin.base import PluginManager, PostPluginProtocol
from pait.util import FuncSig, gen_tip_exc, get_func_sig

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel

__all__ = ["AtMostOneOfPlugin", "AtMostOneOfExtraParam"]


class AtMostOneOfExtraParam(ExtraParam):
    group: str


class AtMostOneOfPlugin(PostPluginProtocol):
    """
    Check whether each group of parameters appear at the same time
    """

    at_most_one_of_list: List[List[str]]

    def check_param(self, context: "PluginContext") -> None:
        try:
            for at_most_one_of in self.at_most_one_of_list:
                if len([i for i in at_most_one_of if context.kwargs.get(i, None) is not None]) > 1:
                    raise CheckValueError(f"requires at most one of param {' or '.join(at_most_one_of)}")
        except Exception as e:
            raise e from gen_tip_exc(context.pait_core_model.func, e)

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        fun_sig: FuncSig = get_func_sig(pait_core_model.func)
        at_most_one_of_dict: Dict[str, List[str]] = {}
        for param in fun_sig.param_list:
            default: Any = param.default
            if not isinstance(default, BaseRequestResourceField):
                continue
            for extra_param in default.extra_param_list:
                if not isinstance(extra_param, AtMostOneOfExtraParam):
                    continue
                at_most_one_of_dict.setdefault(extra_param.group, [])
                at_most_one_of_dict[extra_param.group].append(default.alias or param.name)
        for _, v in at_most_one_of_dict.items():
            kwargs["at_most_one_of_list"].append(v)
        return kwargs

    @classmethod
    def build(cls, *, at_most_one_of_list: Optional[List[List[str]]] = None) -> "PluginManager":  # type: ignore
        return super().build(at_most_one_of_list=at_most_one_of_list or [])

    def __call__(self, context: "PluginContext") -> Any:
        self.check_param(context)
        return super().__call__(context)
