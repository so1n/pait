from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Field

from pait.exceptions import CheckValueError
from pait.field import BaseRequestResourceField, ExtraParam
from pait.plugin.base import PluginManager, PostPluginProtocol
from pait.util import FuncSig, gen_tip_exc, get_func_sig

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel

__all__ = ["RequiredPlugin", "RequiredExtraParam", "RequiredGroupExtraParam"]


class RequiredGroupExtraParam(ExtraParam):
    group: str
    is_main: bool = Field(default=False)


class RequiredExtraParam(ExtraParam):
    main_column: str


class RequiredPlugin(PostPluginProtocol):
    """
    Check dependencies between parameters
    """

    required_dict: Dict[str, List[str]]

    def check_param(self, context: "PluginContext") -> None:
        try:
            for pre_param, param_list in self.required_dict.items():
                if not context.kwargs.get(pre_param, None):
                    continue
                for param in param_list:
                    if context.kwargs.get(param, None) is None:
                        raise CheckValueError(
                            f"{pre_param} requires param {' and '.join(param_list)}, which if not none"
                        )
        except Exception as e:
            raise e from gen_tip_exc(context.pait_core_model.func, e)

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        fun_sig: FuncSig = get_func_sig(pait_core_model.func)
        required_dict: Dict[str, List[str]] = {}
        _temp_group_dict: Dict[str, List[str]] = {}
        _group_main_dict: Dict[str, str] = {}
        for param in fun_sig.param_list:
            default: Any = param.default
            if not isinstance(default, BaseRequestResourceField):
                continue
            for extra_param in default.extra_param_list:
                column_name: str = default.alias or param.name
                if isinstance(extra_param, RequiredExtraParam):
                    required_dict.setdefault(extra_param.main_column, [])
                    required_dict[extra_param.main_column].append(column_name)
                elif isinstance(extra_param, RequiredGroupExtraParam):
                    if extra_param.is_main:
                        _group_main_dict[extra_param.group] = column_name
                    else:
                        _temp_group_dict.setdefault(extra_param.group, [])
                        _temp_group_dict[extra_param.group].append(column_name)
        for group, column_name in _group_main_dict.items():
            required_dict.setdefault(column_name, [])
            required_dict[column_name].extend(_temp_group_dict[group])
        for k, v in required_dict.items():
            kwargs["required_dict"].setdefault(k, [])
            kwargs["required_dict"][k].extend(v)
        return kwargs

    @classmethod
    def build(cls, *, required_dict: Optional[Dict[str, List[str]]] = None) -> "PluginManager":  # type: ignore
        return super().build(required_dict=required_dict or {})

    def __call__(self, context: "PluginContext") -> Any:
        self.check_param(context)
        return super().__call__(context)
