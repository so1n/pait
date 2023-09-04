from dataclasses import MISSING, dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper
    from pait.model.core import PaitCoreModel


__all__ = ["ContextModel"]


@dataclass
class ContextModel(object):
    cbv_instance: Optional[Any]
    app_helper: "BaseAppHelper"
    pait_core_model: "PaitCoreModel"
    # If it is a pre plugin,
    #   args and kwargs are the parameters for the corresponding web framework to call the route.
    # If it is a post plugin,
    #   args and kwargs are the parameters filled in by the developer to write the routing function.
    args: Sequence
    kwargs: dict

    # If it is not used, then it is not initialized, saving memory footprint
    state: Dict[str, Any] = field(init=False)

    def _init_state(self) -> None:
        if not hasattr(self, "state"):
            self.state = {}

    def set_to_state(self, key: str, value: Any) -> None:
        self._init_state()
        self.state[key] = value

    def get_form_state(self, key: str, default_value: Any = MISSING) -> Any:
        value: Any = self.state.get(key, default_value)
        if value is MISSING:
            raise KeyError(key)
        return value


PluginContext = ContextModel
