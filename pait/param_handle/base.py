import inspect
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, Field
from typing_extensions import Self  # type: ignore

from pait import _pydanitc_adapter, field
from pait.exceptions import (
    FieldValueTypeException,
    NotFoundFieldException,
    PaitBaseException,
    ParseTypeError,
    TipException,
)
from pait.plugin.base import PluginProtocol
from pait.types import CallType
from pait.util import FuncSig, gen_tip_exc, get_func_sig, is_bounded_func, is_type

from . import rule
from .util import get_parameter_list_from_class, get_parameter_list_from_pydantic_basemodel

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


_CtxT = TypeVar("_CtxT", bound="ContextModel")


class BaseParamHandler(PluginProtocol, Generic[_CtxT]):
    is_async_mode: bool = False
    tip_exception_class: Optional[Type[TipException]] = TipException
    _pait_pre_load_dc: rule.PreLoadDc
    _pait_cbv_pre_load_prd: rule.ParamRuleDict

    @staticmethod
    def is_self_param(parameter: inspect.Parameter) -> bool:
        if parameter.annotation == Self or parameter.name == "self":
            return True
        return False

    ###############
    # CBV Handler #
    ###############
    @classmethod
    def check_cbv_handler(cls, pait_core_model: "PaitCoreModel", cbv_class: Type) -> None:
        param_list = get_parameter_list_from_class(cbv_class.__class__)
        cls._check_param_field_handler(pait_core_model, cbv_class, param_list)

    @classmethod
    def get_cbv_prd_from_class(cls, pait_core_model: "PaitCoreModel", cbv_class: Type) -> rule.ParamRuleDict:
        param_list = get_parameter_list_from_class(cbv_class)
        prd = cls._param_field_pre_handle(pait_core_model, cbv_class, param_list)
        return prd

    @classmethod
    def add_cbv_prd(cls, pait_core_model: "PaitCoreModel", cbv_class: Type, kwargs: Dict) -> None:
        cbv_prd = cls.get_cbv_prd_from_class(pait_core_model, cbv_class)
        kwargs["_pait_cbv_pre_load_prd"] = cbv_prd

    def get_cbv_prd_from_context(self, context: _CtxT) -> rule.ParamRuleDict:
        # if use pre_load_cbv, then return it
        prd = getattr(self, "_pait_cbv_pre_load_prd", None)
        if prd:
            return prd
        # Due to a problem with the Python decorator mechanism,
        # the cbv prd cannot be obtained when the decorator is initialized,
        # so the prd data is obtained and cached on the first request.
        cbv_prd: Optional[rule.ParamRuleDict] = getattr(context.cbv_instance, "_param_plugin_cbv_prd", None)
        if cbv_prd:
            return cbv_prd
        prd = self.get_cbv_prd_from_class(context.pait_core_model, context.cbv_instance.__class__)
        setattr(context.cbv_instance, "_param_plugin_cbv_prd", prd)
        return prd

    ###################
    # Runtime Handler #
    ###################
    def prd_handle(
        self,
        context: _CtxT,
        _object: Union[FuncSig, Type, None],
        prd: rule.ParamRuleDict,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        raise NotImplementedError()

    def depend_handle(
        self, context: _CtxT, pld: rule.PreLoadDc, func_class_prd: Optional[rule.ParamRuleDict] = None
    ) -> Any:
        pass

    #######################
    # check param handler #
    #######################
    @classmethod
    def check_param_field_by_parameter(
        cls,
        pait_core_model: "PaitCoreModel",
        parameter: inspect.Parameter,
    ) -> None:
        if isinstance(parameter.default, field.Depends):
            func_sig: FuncSig = get_func_sig(parameter.default.func)  # get and cache func sig
            if not is_type(parameter.annotation, func_sig.return_param):
                raise FieldValueTypeException(
                    parameter.name,
                    f"{parameter.name}'s Depends.callable return annotation"
                    f" must:{parameter.annotation}, not {func_sig.return_param}",
                )
        elif isinstance(parameter.default, field.BaseRequestResourceField):
            request_class = pait_core_model.app_helper_class.request_class
            if not getattr(request_class, parameter.default.get_field_name()):
                raise NotFoundFieldException(
                    parameter.name,
                    f"field name: {parameter.default.get_field_name()} not found in {request_class}",
                )  # pragma: no cover
            try:
                check_list: List[Tuple[str, Any]] = [
                    ("default", parameter.default.default),
                    (
                        "example",
                        _pydanitc_adapter.get_field_extra_dict(parameter.default).get(
                            "example", _pydanitc_adapter.PydanticUndefined
                        ),
                    ),
                ]
                if parameter.default.default_factory:
                    check_list.append(("default_factory", parameter.default.default_factory()))
                for title, value in check_list:
                    if getattr(value, "__call__", None):
                        value = value()
                    if value is ...:
                        continue
                    if isinstance(value, _pydanitc_adapter.PydanticUndefinedType):
                        continue
                    if inspect.isclass(parameter.annotation) and isinstance(value, parameter.annotation):
                        continue
                    try:
                        _pydanitc_adapter.PaitModelField(
                            value_name=parameter.name,
                            annotation=parameter.annotation,
                            field_info=Field(...),
                            request_param=parameter.default.get_field_name(),
                        ).validate(value)
                    except Exception:
                        raise ParseTypeError(
                            f"{parameter.name}'s Field.{title} type must {parameter.annotation}. value:{value}"
                        )
            except ParseTypeError as e:
                raise FieldValueTypeException(parameter.name, str(e))
        else:
            if not isinstance(parameter.default, parameter.annotation):
                raise TypeError(parameter.name, f"{parameter.name}'s type error")  # pragma: no cover

    @classmethod
    def _check_func(cls, func: CallType) -> None:
        if inspect.ismethod(func) and not is_bounded_func(func):
            raise ValueError(f"Func: {func} is not a function")

    @classmethod
    def _check_depend_handler(cls, pait_core_model: "PaitCoreModel", func: CallType) -> None:
        """gen depend's pre-load dataclass"""
        cls._check_func(func)
        func_sig: FuncSig = get_func_sig(func, cache_sig=False)
        cls._check_param_field_handler(pait_core_model, func_sig.func, func_sig.param_list)

    @classmethod
    def _check_param_field_handler(
        cls,
        pait_core_model: "PaitCoreModel",
        _object: Any,
        param_list: List["inspect.Parameter"],
    ) -> None:
        for parameter in param_list:
            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseRequestResourceField())
                    cls.check_param_field_by_parameter(pait_core_model, parameter)
                    if isinstance(parameter.default, field.Depends):
                        depend_func = parameter.default.func
                        if inspect.isclass(depend_func):
                            cls._check_param_field_handler(
                                pait_core_model,
                                depend_func,
                                get_parameter_list_from_class(depend_func),
                            )
                elif inspect.isclass(parameter.annotation) and issubclass(parameter.annotation, BaseModel):
                    # support model: model: ModelType
                    cls._check_param_field_handler(
                        pait_core_model,
                        parameter.annotation,
                        get_parameter_list_from_pydantic_basemodel(
                            parameter.annotation, default_field_class=pait_core_model.default_field_class
                        ),
                    )
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=cls.tip_exception_class) from e

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        func_sig: FuncSig = get_func_sig(pait_core_model.func, cache_sig=False)
        for pre_depend in pait_core_model.pre_depend_list:
            cls._check_depend_handler(pait_core_model, pre_depend)
        cls._check_param_field_handler(pait_core_model, func_sig.func, func_sig.param_list)

    ####################
    # pre load handler #
    ####################
    @classmethod
    def _depend_pre_handle(cls, pait_core_model: "PaitCoreModel", func: CallType) -> rule.PreLoadDc:
        """gen depend's pre-load dataclass"""
        cls._check_func(func)
        func_sig: FuncSig = get_func_sig(func, cache_sig=False)
        return rule.PreLoadDc(
            pait_handler=func,  # depend func gen pait handler in pre-load
            param=cls._param_field_pre_handle(pait_core_model, func_sig.func, func_sig.param_list),
        )

    @classmethod
    def _param_field_pre_handle(
        cls,
        pait_core_model: "PaitCoreModel",
        _object: Any,
        param_list: List["inspect.Parameter"],
    ) -> rule.ParamRuleDict:
        """gen param rule dict"""
        param_rule_dict: rule.ParamRuleDict = {}
        for parameter in param_list:
            rule_field_type = rule.empty_ft
            rule_field_type_func_param_dict: dict = {}
            sub_pld = rule.PreLoadDc(pait_handler=rule.empty_pr_func)

            try:
                if parameter.default != parameter.empty:
                    # kwargs param
                    # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseRequestResourceField())
                    if isinstance(parameter.default, field.Depends):
                        sub_pld = cls._depend_pre_handle(pait_core_model, parameter.default.func)
                        rule_field_type = rule.request_depend_ft
                        depend_func = parameter.default.func
                        if inspect.isclass(depend_func):
                            # If this depend func is class, then its class attributes need to be processed
                            rule_field_type_func_param_dict["func_class_prd"] = cls._param_field_pre_handle(
                                pait_core_model,
                                depend_func,
                                get_parameter_list_from_class(depend_func),  # type: ignore
                            )
                    elif isinstance(parameter.default, field.BaseRequestResourceField):
                        rule_field_type = rule.request_field_ft
                        parameter.default.set_request_key(parameter.name)
                        validate_request_value_cb = rule.validate_request_value
                        if pait_core_model.app_helper_class.app_name == "flask":
                            validate_request_value_cb = rule.flask_validate_request_value
                        rule_field_type_func_param_dict.update(
                            # Creating a model field is very performance-intensive (especially for Pydantic V2),
                            # so it needs to be cached
                            pait_model_field=_pydanitc_adapter.PaitModelField(
                                value_name=parameter.name,
                                annotation=parameter.annotation,
                                field_info=parameter.default,
                                request_param=parameter.default.get_field_name(),
                            ),
                            validate_request_value_cb=validate_request_value_cb,
                        )
                elif cls.is_self_param(parameter) and _object is pait_core_model.func:
                    # self param
                    rule_field_type = rule.cbv_class_ft
                elif inspect.isclass(parameter.annotation):
                    # args param
                    if issubclass(
                        parameter.annotation, pait_core_model.app_helper_class.request_class.RequestType  # type: ignore
                    ):
                        # request param
                        rule_field_type = rule.request_ft
                    elif issubclass(parameter.annotation, pait_core_model.app_helper_class.CbvType):
                        # self param
                        rule_field_type = rule.cbv_class_ft
                    elif issubclass(parameter.annotation, BaseModel):
                        # support model: model: ModelType
                        rule_field_type = rule.pait_model_ft
                        param_list = get_parameter_list_from_pydantic_basemodel(
                            parameter.annotation, default_field_class=pait_core_model.default_field_class
                        )
                        sub_pld.param = cls._param_field_pre_handle(pait_core_model, parameter.annotation, param_list)
                        for _parameter in param_list:
                            raw_name = _parameter.name
                            # Each value in PaitModel does not need to valida by `pr func`
                            sub_pld.param[raw_name].param_func = (
                                rule.async_request_field_get_value_pr_func  # type: ignore[assignment]
                                if cls.is_async_mode
                                else rule.request_field_get_value_pr_func
                            )

                            # If the value in Pait Model has alias, then the key of param should be alias
                            real_name = _parameter.default.request_key
                            if raw_name != real_name:
                                sub_pld.param[real_name] = sub_pld.param.pop(raw_name)
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=cls.tip_exception_class) from e
            param_func = rule_field_type.async_func if cls.is_async_mode else rule_field_type.func
            if rule_field_type_func_param_dict:
                param_func = partial(param_func, **rule_field_type_func_param_dict)
            param_rule_dict[parameter.name] = rule.ParamRule(
                name=parameter.name,
                type_=parameter.annotation,
                parameter=parameter,
                param_func=param_func,
                sub=sub_pld,
            )
        return param_rule_dict

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        func_sig: FuncSig = get_func_sig(pait_core_model.func, cache_sig=False)
        pre_load_dc_list = []
        for pre_depend in pait_core_model.pre_depend_list:
            pre_load_dc_list.append(cls._depend_pre_handle(pait_core_model, pre_depend))

        kwargs["_pait_pre_load_dc"] = rule.PreLoadDc(
            pait_handler=func_sig.func,
            pre_depend=pre_load_dc_list,
            param=cls._param_field_pre_handle(pait_core_model, func_sig.func, func_sig.param_list),
        )
        return kwargs
