import asyncio
import inspect
import sys
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseModel
from typing_extensions import Self  # type: ignore

from pait import field
from pait.exceptions import PaitBaseException
from pait.model.context import ContextModel
from pait.param_handle.base import BaseParamHandler, raise_multiple_exc
from pait.plugin.base import PluginContext
from pait.util import (
    FuncSig,
    gen_tip_exc,
    get_func_sig,
    get_parameter_list_from_class,
    get_parameter_list_from_pydantic_basemodel,
)


class AsyncParamHandleContext(PluginContext):
    contextmanager_list: List[Union[AbstractAsyncContextManager, AbstractContextManager]]


class AsyncParamHandler(BaseParamHandler):
    async def param_handle(
        self,
        context: "AsyncParamHandleContext",
        _object: Union[FuncSig, Type],
        param_list: List["inspect.Parameter"],
        pydantic_model: Type[BaseModel] = None,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}
        single_field_dict: Dict["inspect.Parameter", Any] = {}

        for parameter in param_list:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support like: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    if isinstance(parameter.default, field.Depends):
                        kwargs_param_dict[parameter.name] = await self._depend_handle(context, parameter.default.func)
                    else:
                        request_value: Any = self.get_request_value_from_parameter(context, parameter)
                        if asyncio.iscoroutine(request_value) or asyncio.isfuture(request_value):
                            request_value = await request_value
                        self.request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict)
                else:
                    # args param
                    # support model: model: ModelType
                    await self.set_parameter_value_to_args(context, _object, parameter, args_param_list)
            except PaitBaseException as closer_e:
                raise gen_tip_exc(_object, closer_e, parameter, tip_exception_class=self.tip_exception_class)

        # support field: def demo(demo_param: int = pait.field.BaseField())
        if single_field_dict:
            if pydantic_model:
                self.valid_and_merge_kwargs_by_pydantic_model(
                    single_field_dict, kwargs_param_dict, pydantic_model, _object
                )
            else:
                self.valid_and_merge_kwargs_by_single_field_dict(context, single_field_dict, kwargs_param_dict, _object)
        return args_param_list, kwargs_param_dict

    async def set_parameter_value_to_args(
        self,
        context: "AsyncParamHandleContext",
        _object: Union[FuncSig, Type],
        parameter: inspect.Parameter,
        func_args: list,
    ) -> None:
        """use func_args param faster return and extend func_args"""
        if not self._set_parameter_value_to_args(context, parameter, func_args):
            return
        _pait_model: Type[BaseModel] = parameter.annotation
        # Data has been validated or is from a trusted source
        _, kwargs = await self.param_handle(
            context, _object, get_parameter_list_from_pydantic_basemodel(_pait_model), _pait_model
        )
        func_args.append(_pait_model.construct(**kwargs))

    async def _depend_handle(self, context: "AsyncParamHandleContext", func: Any) -> Any:
        class_: Optional[type] = getattr(func, "__class__", None)
        if class_ and not inspect.isfunction(func):
            _, kwargs = await self.param_handle(context, func.__class__, get_parameter_list_from_class(func.__class__))
            func.__dict__.update(kwargs)

        func_sig: FuncSig = get_func_sig(func)
        _func_args, _func_kwargs = await self.param_handle(context, func_sig, func_sig.param_list)
        func_result: Any = func(*_func_args, **_func_kwargs)
        if asyncio.iscoroutine(func_result):
            func_result = await func_result
        if isinstance(func_result, AbstractAsyncContextManager):
            context.contextmanager_list.append(func_result)
            return await func_result.__aenter__()
        elif isinstance(func_result, AbstractContextManager):
            context.contextmanager_list.append(func_result)
            return func_result.__enter__()
        else:
            return func_result

    async def _gen_param(self, context: "AsyncParamHandleContext") -> None:
        # check param from pre depend
        if context.pait_core_model.pre_depend_list:
            await asyncio.gather(
                *[self._depend_handle(context, pre_depend) for pre_depend in context.pait_core_model.pre_depend_list]
            )

        # gen and check param from func
        func_sig: FuncSig = get_func_sig(context.pait_core_model.func)
        context.args, context.kwargs = await self.param_handle(context, func_sig, func_sig.param_list)

        # gen and check param from class
        if context.cbv_param_list:
            _, kwargs = await self.param_handle(context, context.cbv_instance.__class__, context.cbv_param_list)
            context.cbv_instance.__dict__.update(kwargs)
        return None

    async def __call__(self, context: "ContextModel") -> Any:
        error: Optional[Exception] = None
        result: Any = None
        exc_type, exc_val, exc_tb = None, None, None

        param_handle_context: AsyncParamHandleContext = context  # type: ignore
        param_handle_context.contextmanager_list = []
        try:
            await self._gen_param(param_handle_context)
            result = await super().__call__(context)
        except Exception as e:
            error = e
            exc_type, exc_val, exc_tb = sys.exc_info()

        exc_list: List[Exception] = [error] if error else []

        for contextmanager in param_handle_context.contextmanager_list:
            try:
                if isinstance(contextmanager, AbstractContextManager):
                    contextmanager.__exit__(exc_type, exc_val, exc_tb)
                else:
                    await contextmanager.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                exc_list.append(e)

        if exc_list:
            raise_multiple_exc(exc_list)
        else:
            return result


class AsyncConcurrencyParamHandler(AsyncParamHandler):
    async def param_handle(
        self,
        context: "AsyncParamHandleContext",
        _object: Union[FuncSig, Type],
        param_list: List["inspect.Parameter"],
        pydantic_model: Type[BaseModel] = None,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}
        single_field_dict: Dict["inspect.Parameter", Any] = {}

        async def _param_handle(parameter: inspect.Parameter) -> None:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support like: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    if isinstance(parameter.default, field.Depends):
                        kwargs_param_dict[parameter.name] = await self._depend_handle(context, parameter.default.func)
                    else:
                        request_value: Any = self.get_request_value_from_parameter(context, parameter)
                        if asyncio.iscoroutine(request_value) or asyncio.isfuture(request_value):
                            request_value = await request_value
                        self.request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict)
                else:
                    # args param
                    # support model: model: ModelType
                    await self.set_parameter_value_to_args(context, _object, parameter, args_param_list)
            except PaitBaseException as closer_e:
                raise gen_tip_exc(_object, closer_e, parameter, tip_exception_class=self.tip_exception_class)

        if param_list:
            await asyncio.gather(*[_param_handle(parameter) for parameter in param_list])
        # support field: def demo(demo_param: int = pait.field.BaseField())
        if single_field_dict:
            if pydantic_model:
                self.valid_and_merge_kwargs_by_pydantic_model(
                    single_field_dict, kwargs_param_dict, pydantic_model, _object
                )
            else:
                self.valid_and_merge_kwargs_by_single_field_dict(context, single_field_dict, kwargs_param_dict, _object)
        return args_param_list, kwargs_param_dict

    async def __call__(self, context: "ContextModel") -> Any:
        error: Optional[Exception] = None
        result: Any = None
        exc_type, exc_val, exc_tb = None, None, None

        param_handle_context: AsyncParamHandleContext = context  # type: ignore
        param_handle_context.contextmanager_list = []
        try:
            await self._gen_param(param_handle_context)
            result = await super().__call__(context)
        except Exception as e:
            error = e
            exc_type, exc_val, exc_tb = sys.exc_info()

        exc_list: List[Exception] = [error] if error else []

        async def _aexit(contextmanager: Union[AbstractAsyncContextManager, AbstractContextManager]) -> None:
            try:
                if isinstance(contextmanager, AbstractContextManager):
                    contextmanager.__exit__(exc_type, exc_val, exc_tb)
                else:
                    await contextmanager.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                exc_list.append(e)

        if param_handle_context.contextmanager_list:
            await asyncio.gather(
                *[_aexit(contextmanager) for contextmanager in param_handle_context.contextmanager_list]
            )
        if exc_list:
            raise_multiple_exc(exc_list)
        else:
            return result
