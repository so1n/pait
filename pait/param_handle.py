import asyncio
import inspect
import logging
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Generator, List, Optional, Set, Tuple, Type, Union

from pydantic import BaseConfig, BaseModel
from pydantic.fields import Undefined, UndefinedType
from typing_extensions import Self  # type: ignore

from pait import field
from pait.exceptions import (
    FieldValueTypeException,
    NotFoundFieldException,
    NotFoundValueException,
    PaitBaseException,
    ParseTypeError,
    TipException,
)
from pait.field import BaseField
from pait.g import pait_context
from pait.plugin.base import PluginContext, PluginProtocol
from pait.util import (
    FuncSig,
    create_pydantic_model,
    example_value_handle,
    gen_tip_exc,
    get_func_sig,
    get_parameter_list_from_class,
    get_parameter_list_from_pydantic_basemodel,
    ignore_pre_check,
    is_bounded_func,
)

if TYPE_CHECKING:
    from pait.model.context import ContextModel
    from pait.model.core import PaitCoreModel


def raise_multiple_exc(exc_list: List[Exception]) -> None:
    """
    Multiple exceptions may be thrown during the parsing process, and these will be thrown one by one like a stack
    """
    if not exc_list:
        return
    try:
        raise exc_list.pop()
    finally:
        raise_multiple_exc(exc_list)


def parameter_2_dict(
    parameter_value_dict: Dict["inspect.Parameter", Any],
    pydantic_config: Type[BaseConfig],
    validators: Dict[str, classmethod] = None,
) -> Generator[dict, None, None]:
    """Convert all parameters into pydantic mods"""
    annotation_dict: Dict[str, Tuple[Type, Any]] = {}
    param_value_dict: Dict[str, Any] = {}

    # Resolve
    #   the key mismatch between Field.alias and request value
    #   different Fields but same alias
    key_set: Set[str] = set()

    for parameter, value in parameter_value_dict.items():
        param_field = parameter.default
        class_name = parameter.name
        value_key = parameter.default.request_key
        if value_key in key_set:
            yield create_pydantic_model(
                annotation_dict,
                pydantic_config=pydantic_config,
                pydantic_validators=validators,
            )(**param_value_dict).__dict__
            key_set = set()
            annotation_dict = {}
            param_value_dict = {}

        key_set.add(value_key)
        param_value_dict[value_key] = value
        annotation_dict[class_name] = (parameter.annotation, param_field)
    yield create_pydantic_model(
        annotation_dict,
        pydantic_config=pydantic_config,
        pydantic_validators=validators,
    )(**param_value_dict).__dict__


class BaseParamHandler(PluginProtocol):
    tip_exception_class: Optional[Type[TipException]] = TipException

    # def __post_init__(self, pait_core_model: "PaitCoreModel", args: tuple, kwargs: dict) -> None:
    #     super(BaseParamHandler, self).__post_init__(pait_core_model, args, kwargs)

    #     # cbv handle
    #     context_model: "ContextModel" = pait_context.get()
    #     self.cbv_instance: Optional[Any] = context_model.cbv_instance
    #     self._app_helper: "BaseAppHelper" = context_model.app_helper
    #     self.cbv_type: Optional[Type] = None

    #     if self.cbv_instance:
    #         self.cbv_type = self.cbv_instance.__class__
    #         self.cbv_param_list: List["inspect.Parameter"] = get_parameter_list_from_class(self.cbv_type)
    #     else:
    #         self.cbv_param_list = []
    #         # cbv_type = getattr(
    #               inspect.getmodule(func),
    #               func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
    #               )
    #     self.pre_depend_list: List[Callable] = pait_core_model.pre_depend_list
    #     self.pydantic_model_config: Type[BaseConfig] = pait_core_model.pydantic_model_config

    @classmethod
    def check_depend_handle(cls, func: Callable) -> Any:
        if inspect.ismethod(func) and not is_bounded_func(func):
            raise ValueError(f"Method: {func.__qualname__} is not a bounded function")  # pragma: no cover
        func_sig: FuncSig = get_func_sig(func)  # get and cache func sig
        cls.check_param_field_handle(func_sig, func_sig.param_list)

    @staticmethod
    def check_field_type(value: Any, target_type: Any, error_msg: str) -> None:
        if isinstance(value, UndefinedType):
            return
        if getattr(value, "__call__", None):
            value = value()
        try:
            create_pydantic_model({"faker_param_name": (target_type, ...)})(faker_param_name=value)
        except Exception:
            raise ParseTypeError(error_msg)

    @classmethod
    def check_param_field_by_parameter(
        cls,
        parameter: inspect.Parameter,
    ) -> None:
        if isinstance(parameter.default, field.Depends):
            cls.check_depend_handle(parameter.default.func)
        elif isinstance(parameter.default, field.BaseField):
            if not parameter.default.alias:
                parameter.default.request_key = parameter.name
            if ignore_pre_check:
                return
            if parameter.default.alias and not isinstance(parameter.default.alias, str):
                raise FieldValueTypeException(
                    parameter.name,
                    f"{parameter.name}'s Field.alias type must str. value: {parameter.default.alias}",
                )
            try:
                cls.check_field_type(
                    parameter.default.default,
                    parameter.annotation,
                    f"{parameter.name}'s Field.default type must {parameter.annotation}."
                    f" value:{parameter.default.default}",
                )
                if parameter.default.default_factory:
                    cls.check_field_type(
                        parameter.default.default_factory(),
                        parameter.annotation,
                        f"{parameter.name}'s Field.default_factory type must {parameter.annotation}."
                        f" value:{parameter.default.default_factory()}",
                    )
                example_value: Any = parameter.default.extra.get("example", Undefined)
                cls.check_field_type(
                    example_value_handle(example_value),
                    parameter.annotation,
                    f"{parameter.name}'s Field.example type must {parameter.annotation} not {example_value}",
                )
            except ParseTypeError as e:
                raise FieldValueTypeException(parameter.name, str(e))
        else:
            raise NotFoundFieldException(parameter.name, f"{parameter.name}'s Field not found")  # pragma: no cover

    @classmethod
    def check_param_field_handle(
        cls,
        _object: Union[FuncSig, Type, None],
        param_list: List["inspect.Parameter"],
    ) -> None:

        for parameter in param_list:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    cls.check_param_field_by_parameter(parameter)
                else:
                    # args param
                    # support model: model: ModelType
                    if parameter.annotation == Self:
                        continue
                    if not issubclass(parameter.annotation, BaseModel):
                        continue
                    # cache and get parameter_list
                    param_list = get_parameter_list_from_pydantic_basemodel(parameter.annotation)
                    for _parameter in param_list:
                        cls.check_param_field_by_parameter(_parameter)
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=cls.tip_exception_class) from e

    @classmethod
    def pre_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        # check and load param from pre depend
        for pre_depend in pait_core_model.pre_depend_list:
            cls.check_depend_handle(pre_depend)

        # check and load param from func
        func_sig: FuncSig = get_func_sig(pait_core_model.func)
        cls.check_param_field_handle(func_sig, func_sig.param_list)

        # TODO support cbv class Attribute
        # I don't know how to get the class of the decorated function at the initialization of the decorator,
        # which may be an unattainable requirement

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        if ignore_pre_check:
            # pre_check has helped to do the same task as pre_load
            cls.pre_hook(pait_core_model, kwargs)  # pragma: no cover
        return kwargs

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        cls.pre_hook(pait_core_model, kwargs)

    def _set_parameter_value_to_args(
        self, context: "ContextModel", parameter: inspect.Parameter, func_args: list
    ) -> bool:
        """Extract the self parameter of the cbv handler,
        the request parameter of the route and the parameter of type PaitBaseModel,
        and check if there are any other parameters that do not meet the conditions

        Sort by frequency of occurrence
        """
        if context.cbv_instance and (
            parameter.annotation == Self or (not func_args and parameter.annotation == parameter.empty)
        ):
            # first parma must self param, looking forward to the appearance of `self type
            func_args.append(context.cbv_instance)
        elif issubclass(parameter.annotation, BaseModel):
            return True
        elif context.app_helper.request.check_request_type(parameter.annotation):
            # support request param(def handle(request: Request))
            func_args.append(context.app_helper.request.request)
        else:
            logging.warning(f"Pait not support args: {parameter}")  # pragma: no cover
        return False

    @staticmethod
    def request_value_handle(
        parameter: inspect.Parameter,
        request_value: Any,
        base_model_dict: Dict[str, Any],
        parameter_value_dict: Dict["inspect.Parameter", Any],
    ) -> None:
        """parse request_value and set to base_model_dict or parameter_value_dict"""
        pait_field: BaseField = parameter.default
        if request_value is None:
            if pait_field.not_value_exception:
                raise pait_field.not_value_exception
            raise NotFoundValueException(parameter.name, f"Can not found {parameter.name} value")
        annotation: Type[BaseModel] = parameter.annotation

        # some type like dict, but not isinstance Mapping, e.g: werkzeug.datastructures.EnvironHeaders
        # assert getattr(request_value, "get", None), f"{parameter.name}'s request value must like dict"
        if not pait_field.raw_return:

            request_value = pait_field.request_value_handle(request_value)
            if request_value is Undefined:
                if pait_field.not_value_exception:
                    raise pait_field.not_value_exception
                raise NotFoundValueException(parameter.name, f"Can not found {parameter.name} value")

        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            # parse annotation is pydantic.BaseModel and base_model_dict not None
            base_model_dict[parameter.name] = annotation(**request_value)
        else:
            # parse annotation is python type and pydantic.field
            parameter_value_dict[parameter] = request_value

    def get_request_value_from_parameter(
        self, context: "ContextModel", parameter: inspect.Parameter
    ) -> Union[Any, Coroutine]:
        field_name: str = parameter.default.get_field_name()
        # Note: not use hasattr with LazyProperty (
        #   because hasattr will calling getattr(obj, name) and catching AttributeError,
        # )
        app_field_func: Optional[Callable] = getattr(context.app_helper.request, field_name, None)
        if app_field_func is None:
            raise NotFoundFieldException(
                parameter.name, f"field: {field_name} not found in {context.app_helper.request}"
            )  # pragma: no cover
        return app_field_func()

    def valid_and_merge_kwargs_by_single_field_dict(
        self,
        context: "ContextModel",
        single_field_dict: Dict["inspect.Parameter", Any],
        kwargs_param_dict: Dict[str, Any],
        _object: Union[FuncSig, Type, None],
    ) -> None:
        for parse_dict in parameter_2_dict(single_field_dict, context.pait_core_model.pydantic_model_config):
            kwargs_param_dict.update(parse_dict)

    @staticmethod
    def valid_and_merge_kwargs_by_pydantic_model(
        single_field_dict: Dict["inspect.Parameter", Any],
        kwargs_param_dict: Dict[str, Any],
        pydantic_model: Type[BaseModel],
        _object: Union[FuncSig, Type, None],
    ) -> None:
        request_dict: Dict[str, Any] = kwargs_param_dict.copy()
        for k, v in single_field_dict.items():
            request_dict[k.default.request_key] = v
        kwargs_param_dict.update(pydantic_model(**request_dict))


class ParamHandler(BaseParamHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._contextmanager_list: List[AbstractContextManager] = []

    def param_handle(
        self,
        context: "ContextModel",
        _object: Union[FuncSig, Type, None],
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
                    # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    if isinstance(parameter.default, field.Depends):
                        kwargs_param_dict[parameter.name] = self._depend_handle(context, parameter.default.func)
                    else:
                        request_value: Any = self.get_request_value_from_parameter(context, parameter)
                        self.request_value_handle(parameter, request_value, kwargs_param_dict, single_field_dict)
                else:
                    # args param
                    # support model: model: ModelType
                    self.set_parameter_value_to_args(context, parameter, args_param_list)
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=self.tip_exception_class)
        # support field: def demo(demo_param: int = pait.field.BaseField())
        if single_field_dict:
            if pydantic_model:
                self.valid_and_merge_kwargs_by_pydantic_model(
                    single_field_dict, kwargs_param_dict, pydantic_model, _object
                )
            else:
                self.valid_and_merge_kwargs_by_single_field_dict(context, single_field_dict, kwargs_param_dict, _object)
        return args_param_list, kwargs_param_dict

    def set_parameter_value_to_args(
        self, context: "ContextModel", parameter: inspect.Parameter, func_args: list
    ) -> None:
        """use func_args param faster return and extend func_args"""
        if not self._set_parameter_value_to_args(context, parameter, func_args):
            return
        # support pait_model param(def handle(model: PaitBaseModel))
        _pait_model: Type[BaseModel] = parameter.annotation
        _, kwargs = self.param_handle(
            context, None, get_parameter_list_from_pydantic_basemodel(_pait_model), pydantic_model=_pait_model
        )
        # Data has been validated or is from a trusted source
        func_args.append(_pait_model.construct(**kwargs))

    def _depend_handle(self, context: "ContextModel", func: Any) -> Any:
        class_: Optional[type] = getattr(func, "__class__", None)
        if class_ and not inspect.isfunction(func):
            _, kwargs = self.param_handle(context, func.__class__, get_parameter_list_from_class(func.__class__))
            func.__dict__.update(kwargs)

        func_sig: FuncSig = get_func_sig(func)
        _func_args, _func_kwargs = self.param_handle(context, func_sig, func_sig.param_list)
        func_result: Any = func(*_func_args, **_func_kwargs)
        if isinstance(func_result, AbstractContextManager):
            self._contextmanager_list.append(func_result)
            return func_result.__enter__()
        else:
            return func_result

    def _gen_param(self, context: "ContextModel") -> None:
        # check param from pre depend
        for pre_depend in context.pait_core_model.pre_depend_list:
            self._depend_handle(context, pre_depend)

        # gen and check param from func
        func_sig: FuncSig = get_func_sig(context.pait_core_model.func)
        context.args, context.kwargs = self.param_handle(context, func_sig, func_sig.param_list)

        # gen and check param from class
        if context.cbv_param_list:
            _, kwargs = self.param_handle(context, context.cbv_instance.__class__, context.cbv_param_list)
            context.cbv_instance.__dict__.update(kwargs)
        return None

    def __call__(self, context: PluginContext) -> Any:
        with self:
            return super().__call__(context)

    def __enter__(self) -> "ParamHandler":
        self._gen_param(pait_context.get())
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        exc_list: List[Exception] = []
        for contextmanager in self._contextmanager_list:
            try:
                contextmanager.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                exc_list.append(e)
            else:
                if exc_type and issubclass(exc_type, Exception):
                    exc_list.append(exc_type(exc_val).with_traceback(exc_tb))
        if exc_list:
            raise_multiple_exc(exc_list)

            return True
        else:
            return False


class AsyncParamHandler(BaseParamHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._contextmanager_list: List[Union[AbstractAsyncContextManager, AbstractContextManager]] = []

    async def param_handle(
        self,
        context: "ContextModel",
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

    async def set_parameter_value_to_args(
        self, context: "ContextModel", _object: Union[FuncSig, Type], parameter: inspect.Parameter, func_args: list
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

    async def _depend_handle(self, context: "ContextModel", func: Any) -> Any:
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
            self._contextmanager_list.append(func_result)
            return await func_result.__aenter__()
        elif isinstance(func_result, AbstractContextManager):
            self._contextmanager_list.append(func_result)
            return func_result.__enter__()
        else:
            return func_result

    async def _gen_param(self, context: "ContextModel") -> None:
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
        async with self:
            try:
                return await super().__call__(context)
            except Exception as e:
                raise e

    async def __aenter__(self) -> "AsyncParamHandler":
        await self._gen_param(pait_context.get())
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        exc_list: List[Exception] = []

        async def _aexit(contextmanager: Union[AbstractAsyncContextManager, AbstractContextManager]) -> None:
            try:
                if isinstance(contextmanager, AbstractContextManager):
                    contextmanager.__exit__(exc_type, exc_val, exc_tb)
                else:
                    await contextmanager.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                exc_list.append(e)
            else:
                if exc_type and issubclass(exc_type, Exception):
                    exc_list.append(exc_type(exc_val).with_traceback(exc_tb))

        if self._contextmanager_list:
            await asyncio.gather(*[_aexit(contextmanager) for contextmanager in self._contextmanager_list])
        if exc_list:
            raise_multiple_exc(exc_list)
            return True
        else:
            return False
