import asyncio
import inspect
import sys
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Dict, List, Optional, Tuple, Union

from typing_extensions import Self  # type: ignore

from pait.exceptions import PaitBaseException
from pait.model.context import ContextModel
from pait.param_handle import rule
from pait.param_handle.base import BaseParamHandler, raise_multiple_exc
from pait.util import gen_tip_exc, get_pait_handler


class AsyncParamHandleContext(ContextModel):
    contextmanager_list: List[Union[AbstractAsyncContextManager, AbstractContextManager]]


class AsyncParamHandler(BaseParamHandler[AsyncParamHandleContext]):
    _is_async = True

    async def prd_handle(  # type: ignore[override]
        self,
        context: "AsyncParamHandleContext",
        _object: Any,
        prd: rule.ParamRuleDict,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}

        for param_name, pr in prd.items():
            try:
                value = pr.param_func(pr, context, self)
                if value is rule.MISSING:
                    continue
                if asyncio.iscoroutine(value) or asyncio.isfuture(value) or asyncio.iscoroutinefunction(value):
                    value = await value
                if pr.parameter.default is pr.parameter.empty:
                    args_param_list.append(value)
                else:
                    kwargs_param_dict[param_name] = value
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, pr.parameter, tip_exception_class=self.tip_exception_class)

        return args_param_list, kwargs_param_dict

    async def depend_handle(
        self,
        context: "AsyncParamHandleContext",
        pld: "rule.PreLoadDc",
        func_class_prd: Optional[rule.ParamRuleDict] = None,
    ) -> Any:
        pait_handler = pld.pait_handler
        if inspect.isclass(pait_handler):
            # support depend type is class
            assert (
                func_class_prd
            ), f"`func_class_prd` param must not none, please check {self.__class__}.pre_load_hook method"
            _, kwargs = await self.prd_handle(context, pait_handler, func_class_prd)
            pait_handler = pait_handler()
            pait_handler.__dict__.update(kwargs)

        # Get the real pait_handler of the depend class
        pait_handler = get_pait_handler(pait_handler)
        _func_args, _func_kwargs = await self.prd_handle(context, pait_handler, pld.param)
        func_result: Any = pait_handler(*_func_args, **_func_kwargs)
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
        for index, pre_depend in enumerate(context.pait_core_model.pre_depend_list):
            await self.depend_handle(context, self._pait_pre_load_dc.pre_depend[index])

        context.args, context.kwargs = await self.prd_handle(
            context, self._pait_pre_load_dc.pait_handler, self._pait_pre_load_dc.param
        )

        if context.cbv_instance:
            prd = self.get_cbv_prd(context)
            _, kwargs = await self.prd_handle(context, context.cbv_instance.__class__, prd)
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
