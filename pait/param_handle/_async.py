import asyncio
import inspect
import sys
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Coroutine, Dict, List, Mapping, Optional, Tuple, Type, Union

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
        pydantic_model: Optional[Type[BaseModel]] = None,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}

        for parameter in param_list:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support like: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    if isinstance(parameter.default, field.Depends):
                        kwargs_param_dict[parameter.name] = await self._depend_handle(context, parameter.default.func)
                    else:
                        request_value: Union[Mapping, Coroutine[Any, Any, Mapping]] = getattr(
                            context.app_helper.request, parameter.default.get_field_name(), lambda: {}
                        )()
                        if asyncio.iscoroutine(request_value) or asyncio.isfuture(request_value):
                            request_value = await request_value
                        self.request_value_handle(
                            parameter, request_value, kwargs_param_dict, pydantic_model  # type: ignore[arg-type]
                        )
                else:
                    # args param
                    # support model: model: ModelType
                    await self.set_parameter_value_to_args(context, _object, parameter, args_param_list)
            except PaitBaseException as closer_e:
                raise gen_tip_exc(_object, closer_e, parameter, tip_exception_class=self.tip_exception_class)
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
        _, kwargs = await self.param_handle(
            context,
            _object,
            get_parameter_list_from_pydantic_basemodel(_pait_model, context.pait_core_model.default_field_class),
            _pait_model,
        )
        func_args.append(_pait_model(**kwargs))

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
            for pre_depend in context.pait_core_model.pre_depend_list:
                await self._depend_handle(context, pre_depend)

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
