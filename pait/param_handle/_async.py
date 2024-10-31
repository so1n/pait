import asyncio
import inspect
import sys
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from typing_extensions import Self  # type: ignore

from pait.exceptions import PaitBaseException
from pait.field import resource_parse
from pait.model.context import ContextModel
from pait.param_handle.base import BaseParamHandler, raise_multiple_exc
from pait.util import gen_tip_exc, get_pait_handler, to_thread


class AsyncParamHandleContext(ContextModel):
    contextmanager_list: List[Union[AbstractAsyncContextManager, AbstractContextManager]]


async def run_func(context: "AsyncParamHandleContext", func: Callable, *args: Any, **kwargs: Any) -> Any:
    if asyncio.iscoroutinefunction(func):
        func_result = await func(*args, **kwargs)
    elif context.pait_core_model.sync_to_thread:
        func_result = await to_thread(func, *args, **kwargs)
    else:
        func_result = func(*args, **kwargs)
        if asyncio.iscoroutine(func_result):
            # bound method is not coroutine function, but result is coroutine object
            func_result = await func_result
    return func_result


class AsyncParamHandler(BaseParamHandler[AsyncParamHandleContext]):
    is_async_mode = True

    async def prd_handle(  # type: ignore[override]
        self,
        context: "AsyncParamHandleContext",
        _object: Any,
        prd: resource_parse.ParseResourceParamDcDict,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args_param_list: List[Any] = []
        kwargs_param_dict: Dict[str, Any] = {}

        for param_name, pr in prd.items():
            try:
                value = pr.parse_resource_func(pr, context, self)
                if asyncio.iscoroutine(value) or asyncio.isfuture(value) or asyncio.iscoroutinefunction(value):
                    value = await value
                elif context.pait_core_model.sync_to_thread and inspect.isfunction(value):
                    value = await to_thread(value)

                if pr.parameter.default is pr.parameter.empty:
                    args_param_list.append(value)
                else:
                    kwargs_param_dict[param_name] = value
            except PaitBaseException as e:
                raise gen_tip_exc(
                    _object, e, pr.parameter, tip_exception_class=self.pait_core_model.tip_exception_class
                )

        return args_param_list, kwargs_param_dict

    async def depend_handle(
        self,
        context: "AsyncParamHandleContext",
        pld: "resource_parse.PreLoadDc",
    ) -> Any:
        pait_handler = pld.call_handler
        if inspect.isclass(pait_handler):
            # support depend type is class
            assert (
                pld.cbv_param
            ), f"`func_class_prd` param must not none, please check {self.__class__}.pre_load_hook method"
            _, kwargs = await self.prd_handle(context, pait_handler, pld.cbv_param)
            pait_handler = pait_handler()
            pait_handler.__dict__.update(kwargs)

        # Get the real pait_handler of the depend class
        pait_handler = get_pait_handler(pait_handler)
        _func_args, _func_kwargs = await self.prd_handle(context, pait_handler, pld.param)
        func_result = await run_func(context, pait_handler, *_func_args, **_func_kwargs)
        if isinstance(func_result, AbstractAsyncContextManager):
            context.contextmanager_list.append(func_result)
            return await func_result.__aenter__()
        elif isinstance(func_result, AbstractContextManager):
            context.contextmanager_list.append(func_result)
            return await run_func(context, func_result.__enter__)
        else:
            return func_result

    async def _gen_param(self, context: "AsyncParamHandleContext") -> None:
        # check param from pre depend
        for pre_depend_dc in self._pait_pre_depend_dc:
            await self.depend_handle(context, pre_depend_dc)

        context.args, context.kwargs = await self.prd_handle(
            context, self._pait_pre_load_dc.call_handler, self._pait_pre_load_dc.param
        )

        if context.cbv_instance:
            prd = self.get_cbv_prd_from_context(context)
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
            result = await run_func(param_handle_context, super().__call__, context)
        except Exception as e:
            error = e
            exc_type, exc_val, exc_tb = sys.exc_info()

        exc_list: List[Exception] = [error] if error else []

        for contextmanager in param_handle_context.contextmanager_list:
            try:
                if isinstance(contextmanager, AbstractContextManager):
                    await run_func(param_handle_context, contextmanager.__exit__, exc_type, exc_val, exc_tb)
                else:
                    await contextmanager.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:  # pragma: no cover
                exc_list.append(e)  # pragma: no cover

        if exc_list:
            raise_multiple_exc(exc_list)
        else:
            return result
