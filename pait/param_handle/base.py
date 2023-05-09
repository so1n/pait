import inspect
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Type, Union

from pydantic import BaseConfig, BaseModel
from pydantic.error_wrappers import ValidationError
from pydantic.fields import ModelField, Undefined, UndefinedType
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
from pait.plugin.base import PluginProtocol
from pait.util import (
    FuncSig,
    create_pydantic_model,
    example_value_handle,
    gen_tip_exc,
    get_func_sig,
    get_parameter_list_from_pydantic_basemodel,
    ignore_pre_check,
    is_bounded_func,
    is_type,
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
    def check_depend_handle(cls, pait_core_model: "PaitCoreModel", func: Callable) -> Any:
        if inspect.ismethod(func) and not is_bounded_func(func):
            raise ValueError(f"Method: {func.__qualname__} is not a bounded function")  # pragma: no cover
        func_sig: FuncSig = get_func_sig(func)  # get and cache func sig
        cls.check_param_field_handle(pait_core_model, func_sig, func_sig.param_list)

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
        pait_core_model: "PaitCoreModel",
        parameter: inspect.Parameter,
    ) -> None:
        if isinstance(parameter.default, field.Depends):
            cls.check_depend_handle(pait_core_model, parameter.default.func)
            if ignore_pre_check:
                return
            func_sig: FuncSig = get_func_sig(parameter.default.func)  # get and cache func sig
            if not is_type(parameter.annotation, func_sig.return_param):
                raise FieldValueTypeException(
                    parameter.name,
                    f"{parameter.name}'s Depends.callable return annotation"
                    f" must:{parameter.annotation}, not {func_sig.return_param}",
                )
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
            if parameter.default.get_field_name() not in pait_core_model.app_helper_class.request_class.__dict__:
                raise NotFoundFieldException(
                    parameter.name,
                    f"field name: {parameter.default.get_field_name()}"
                    f" not found in {pait_core_model.app_helper_class.request_class}",
                )  # pragma: no cover
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
        pait_core_model: "PaitCoreModel",
        _object: Union[FuncSig, Type, None],
        param_list: List["inspect.Parameter"],
    ) -> None:
        for parameter in param_list:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseField())
                    cls.check_param_field_by_parameter(pait_core_model, parameter)
                else:
                    # args param
                    # support model: model: ModelType
                    if parameter.annotation == Self:
                        continue
                    if not (inspect.isclass(parameter.annotation) and issubclass(parameter.annotation, BaseModel)):
                        continue
                    # cache and get parameter_list
                    param_list = get_parameter_list_from_pydantic_basemodel(
                        parameter.annotation, default_field_class=pait_core_model.default_field_class
                    )
                    for _parameter in param_list:
                        cls.check_param_field_by_parameter(pait_core_model, _parameter)
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=cls.tip_exception_class) from e

    @classmethod
    def pre_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        # check and load param from pre depend
        for pre_depend in pait_core_model.pre_depend_list:
            cls.check_depend_handle(pait_core_model, pre_depend)

        # check and load param from func
        func_sig: FuncSig = get_func_sig(pait_core_model.func)
        cls.check_param_field_handle(pait_core_model, func_sig, func_sig.param_list)

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
        elif inspect.isclass(parameter.annotation) and issubclass(parameter.annotation, BaseModel):
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
        request_value: Mapping,
        kwargs_param_dict: Dict[str, Any],
        pydantic_model: Optional[Type[BaseModel]] = None,
    ) -> None:
        """parse request_value and set to base_model_dict or parameter_value_dict"""
        pait_field: BaseField = parameter.default
        annotation: Type[BaseModel] = parameter.annotation

        if not pait_field.raw_return:
            request_value = pait_field.request_value_handle(request_value)
            if request_value is Undefined:
                raise (
                    pait_field.not_value_exception
                    or NotFoundValueException(parameter.name, f"Can not found {parameter.name} value")
                )
        if pydantic_model:
            # If it belongs to the field of the PaitModel,
            # it does not need to be verified, but is returned to the PaitModel for processing
            kwargs_param_dict[pait_field.request_key] = request_value
        elif inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            # parse annotation is pydantic.BaseModel and base_model_dict not None
            kwargs_param_dict[parameter.name] = annotation(**request_value)
        else:
            # parse annotation is python type and pydantic.field
            request_value, e = ModelField(
                name=parameter.name,
                type_=parameter.annotation,
                model_config=BaseConfig,
                field_info=pait_field,
                class_validators={},
                # Since the corresponding value has already been processed, there is no need to process it again
                # default: Any = None,
                # default_factory: Optional[NoArgAnyCallable] = None,
                # required: 'BoolUndefined' = Undefined,
                # final: bool = False,
                # alias: Optional[str] = None,
            ).validate(request_value, kwargs_param_dict, loc=pait_field.get_field_name())
            if e:
                raise ValidationError(e, BaseModel)
            kwargs_param_dict[parameter.name] = request_value
