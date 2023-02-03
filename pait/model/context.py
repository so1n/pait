from dataclasses import dataclass, field
from inspect import Parameter
from typing import TYPE_CHECKING, Any, List, Optional, Sequence

from pait.util import get_parameter_list_from_class

if TYPE_CHECKING:
    from pait.app.base import BaseAppHelper
    from pait.model.core import PaitCoreModel


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

    cbv_param_list: List[Parameter] = field(init=False)

    def __post_init__(self) -> None:
        if self.cbv_instance:
            self.cbv_param_list = get_parameter_list_from_class(self.cbv_instance.__class__)
        else:
            self.cbv_param_list = []