import inspect
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Type, Union

import gevent
from pydantic import BaseModel

from pait import field
from pait.exceptions import PaitBaseException
from pait.param_handle import ParamHandler, parameter_2_dict
from pait.util import FuncSig, enable_gevent, gen_tip_exc, get_func_sig, get_parameter_list_from_pydantic_basemodel

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel


class GeventParamHandler(ParamHandler):
    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not enable_gevent():
            raise PaitBaseException(f"{cls.__name__} is not supported in this environment.")

    def param_handle(
        self,
        _object: Union[FuncSig, Type, None],
        param_list: List["inspect.Parameter"],
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}

        single_field_dict: Dict["inspect.Parameter", Any] = {}

        def _param_handle(parameter: inspect.Parameter) -> Callable:
            def _spwan_param_handler() -> None:
                try:
                    if parameter.default != parameter.empty:
                        # kwargs param
                        # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                        if isinstance(parameter.default, field.Depends):
                            kwargs_param_dict[parameter.name] = self._depend_handle(parameter.default.func)
                        else:
                            request_value: Any = self.get_request_value_from_parameter(parameter)
                            self.request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict)
                    else:
                        # args param
                        # support model: model: ModelType
                        self.set_parameter_value_to_args(parameter, args_param_list)
                except PaitBaseException as e:
                    raise gen_tip_exc(_object, e, parameter)

            return _spwan_param_handler

        gevent.joinall([gevent.spawn(_param_handle(parameter)) for parameter in param_list])
        # support field: def demo(demo_param: int = pait.field.BaseField())
        if single_field_dict:
            try:
                for parse_dict in parameter_2_dict(single_field_dict, self.pydantic_model_config):
                    kwargs_param_dict.update(parse_dict)
            except Exception as e:
                raise e from gen_tip_exc(_object, e)
        return args_param_list, kwargs_param_dict

    def set_parameter_value_to_args(self, parameter: inspect.Parameter, func_args: list) -> None:
        """use func_args param faster return and extend func_args"""
        if not self._set_parameter_value_to_args(parameter, func_args):
            return
        # support pait_model param(def handle(model: PaitBaseModel))
        _pait_model: Type[BaseModel] = parameter.annotation
        _, kwargs = self.param_handle(None, get_parameter_list_from_pydantic_basemodel(_pait_model))
        # Data has been validated or is from a trusted source
        func_args.append(_pait_model.construct(**kwargs))

    def _depend_handle(self, func: Callable) -> Any:
        func_sig: FuncSig = get_func_sig(func)
        _func_args, _func_kwargs = self.param_handle(func_sig, func_sig.param_list)
        func_result: Any = func(*_func_args, **_func_kwargs)
        if isinstance(func_result, AbstractContextManager):
            self._contextmanager_list.append(func_result)
            return func_result.__enter__()
        else:
            return func_result

    def _gen_param(self) -> None:
        # check param from pre depend
        def _depend_handler(pre_depend: Callable) -> Callable:
            def _spwan_depend_handler() -> None:
                self._depend_handle(pre_depend)

            return _spwan_depend_handler

        gevent.joinall([gevent.spawn(_depend_handler(pre_depend)) for pre_depend in self.pre_depend_list])

        # gen and check param from func
        func_sig: FuncSig = get_func_sig(self.pait_core_model.func)
        self.args, self.kwargs = self.param_handle(func_sig, func_sig.param_list)

        # gen and check param from class
        if self.cbv_param_list and self.cbv_type:
            _, kwargs = self.param_handle(self.cbv_type, self.cbv_param_list)
            self.cbv_instance.__dict__.update(kwargs)
        return None
