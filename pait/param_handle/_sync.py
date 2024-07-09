import inspect
import sys
from contextlib import AbstractContextManager
from typing import Any, Dict, List, Optional, Tuple

from typing_extensions import Self  # type: ignore

from pait.exceptions import PaitBaseException
from pait.model.context import ContextModel
from pait.param_handle.base import BaseParamHandler, raise_multiple_exc, rule
from pait.util import gen_tip_exc, get_pait_handler


class ParamHandleContext(ContextModel):
    contextmanager_list: List[AbstractContextManager]


class ParamHandler(BaseParamHandler[ParamHandleContext]):
    def prd_handle(
        self, context: "ParamHandleContext", _object: Any, prd: rule.ParamRuleDict,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}

        for param_name, pr in prd.items():
            try:
                value = pr.param_func(pr, context, self)
                if value is rule.MISSING:
                    continue
                if pr.parameter.default is pr.parameter.empty:
                    args_param_list.append(value)
                else:
                    kwargs_param_dict[param_name] = value
            except PaitBaseException as e:
                raise gen_tip_exc(
                    _object, e, pr.parameter, tip_exception_class=self.pait_core_model.tip_exception_class
                )

        return args_param_list, kwargs_param_dict

    def depend_handle(self, context: "ParamHandleContext", pld: "rule.PreLoadDc",) -> Any:
        pait_handler = pld.pait_handler
        if inspect.isclass(pait_handler):
            # support depend type is class
            assert (
                pld.func_class_prd
            ), f"`func_class_prd` param must not none, please check {self.__class__}.pre_load_hook method"
            _, kwargs = self.prd_handle(context, pait_handler, pld.func_class_prd)
            pait_handler = pait_handler()
            pait_handler.__dict__.update(kwargs)

        # Get the real pait_handler of the depend class
        pait_handler = get_pait_handler(pait_handler)
        _func_args, _func_kwargs = self.prd_handle(context, pait_handler, pld.param)
        func_result: Any = pait_handler(*_func_args, **_func_kwargs)
        if isinstance(func_result, AbstractContextManager):
            context.contextmanager_list.append(func_result)
            return func_result.__enter__()
        else:
            return func_result

    def _gen_param(self, context: "ParamHandleContext") -> None:
        # check param from pre depend
        for pre_depend_dc in self._pait_pre_depend_dc:
            self.depend_handle(context, pre_depend_dc)

        context.args, context.kwargs = self.prd_handle(
            context, self._pait_pre_load_dc.pait_handler, self._pait_pre_load_dc.param
        )
        if context.cbv_instance:
            prd = self.get_cbv_prd_from_context(context)
            _, kwargs = self.prd_handle(context, context.cbv_instance.__class__, prd)
            context.cbv_instance.__dict__.update(kwargs)
        return None

    def __call__(self, context: ContextModel) -> Any:
        error: Optional[Exception] = None
        result: Any = None
        exc_type, exc_val, exc_tb = None, None, None

        param_handle_context: ParamHandleContext = context  # type: ignore
        param_handle_context.contextmanager_list = []

        try:
            self._gen_param(param_handle_context)
            result = super().__call__(context)
        except Exception as e:
            error = e
            exc_type, exc_val, exc_tb = sys.exc_info()
        exc_list: List[Exception] = [error] if error else []
        for contextmanager in param_handle_context.contextmanager_list:
            try:
                contextmanager.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:  # pragma: no cover
                exc_list.append(e)  # pragma: no cover
        if exc_list:
            raise_multiple_exc(exc_list)
        else:
            return result
