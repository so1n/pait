import inspect
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import Self  # type: ignore

from pait.exceptions import PaitBaseException
from pait.field import BaseField, app, other, resource_parse
from pait.plugin.base import PluginProtocol
from pait.types import CallType
from pait.util import FuncSig, gen_tip_exc, get_func_sig, get_parameter_list_from_class

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
    _pait_pre_load_dc: resource_parse.PreLoadDc
    _pait_pre_depend_dc: List[resource_parse.PreLoadDc]

    @staticmethod
    def is_self_param(parameter: inspect.Parameter) -> bool:
        if parameter.name == "self" or parameter.annotation == Self:
            return True
        return False

    @classmethod
    def get_field_from_parameter(
        cls, pait_core_model: "PaitCoreModel", _object: Any, parameter: inspect.Parameter
    ) -> Optional[Type[BaseField]]:
        maybe_filed = parameter.default
        if maybe_filed is not parameter.empty and isinstance(maybe_filed, BaseField):
            # kwargs param
            # support model: def demo(pydantic.BaseModel: BaseModel = pait.field.BaseRequestResourceField())
            return maybe_filed.__class__
        if cls.is_self_param(parameter) and _object is pait_core_model.func:
            # self param
            return other.CbvField
        elif inspect.isclass(parameter.annotation):
            # args param
            if issubclass(
                parameter.annotation, pait_core_model.app_helper_class.request_class.RequestType  # type: ignore
            ):
                # request param
                return other.RequestField
            elif issubclass(parameter.annotation, pait_core_model.app_helper_class.CbvType):
                # self param
                return other.CbvField
            elif issubclass(parameter.annotation, BaseModel):
                # support model: model: ModelType
                return other.PaitModelField
        return None

    @classmethod
    def get_param_rule_from_parameter_list(
        cls,
        pait_core_model: "PaitCoreModel",
        _object: Any,
        param_list: List["inspect.Parameter"],
    ) -> resource_parse.ParseResourceParamDcDict:
        """gen param rule dict"""
        param_rule_dict: resource_parse.ParseResourceParamDcDict = {}
        for parameter in param_list:
            try:
                base_field_class = cls.get_field_from_parameter(pait_core_model, _object, parameter)
                if not base_field_class:
                    continue
                param_rule_dict[parameter.name] = base_field_class.pre_load(
                    core_model=pait_core_model, parameter=parameter, param_plugin=cls
                )
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=pait_core_model.tip_exception_class) from e
        return param_rule_dict

    ###############
    # CBV Handler #
    ###############
    @classmethod
    def check_cbv_handler(cls, pait_core_model: "PaitCoreModel", cbv_class: Type) -> None:
        cls.param_field_check_handler(pait_core_model, cbv_class, get_parameter_list_from_class(cbv_class.__class__))

    @classmethod
    def get_cbv_prd_from_class(
        cls, pait_core_model: "PaitCoreModel", cbv_class: Type
    ) -> resource_parse.ParseResourceParamDcDict:
        return cls.get_param_rule_from_parameter_list(
            pait_core_model, cbv_class, get_parameter_list_from_class(cbv_class)
        )

    @classmethod
    def add_cbv_prd(cls, pait_core_model: "PaitCoreModel", cbv_class: Type, kwargs: Dict) -> None:
        cbv_prd = cls.get_cbv_prd_from_class(pait_core_model, cbv_class)
        kwargs["_pait_cbv_pre_load_prd"] = cbv_prd

    def get_cbv_prd_from_context(self, context: _CtxT) -> resource_parse.ParseResourceParamDcDict:
        # if use pre_load_cbv, then return it
        prd = getattr(self, "_pait_cbv_pre_load_prd", None)
        if prd:
            return prd
        # Due to a problem with the Python decorator mechanism,
        # the cbv prd cannot be obtained when the decorator is initialized,
        # so the prd data is obtained and cached on the first request.
        cbv_prd: Optional[resource_parse.ParseResourceParamDcDict] = getattr(
            context.cbv_instance, "_param_plugin_cbv_prd", None
        )
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
        prd: resource_parse.ParseResourceParamDcDict,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        raise NotImplementedError()

    def depend_handle(self, context: _CtxT, pld: resource_parse.PreLoadDc) -> Any:
        pass

    #######################
    # check param handler #
    #######################
    @classmethod
    def param_field_check_handler(
        cls,
        pait_core_model: "PaitCoreModel",
        _object: Any,
        param_list: List["inspect.Parameter"],
    ) -> None:
        for parameter in param_list:
            try:
                base_field_class = cls.get_field_from_parameter(pait_core_model, _object, parameter)
                if base_field_class:
                    base_field_class.pre_check(core_model=pait_core_model, parameter=parameter, param_plugin=cls)
            except PaitBaseException as e:
                raise gen_tip_exc(_object, e, parameter, tip_exception_class=pait_core_model.tip_exception_class) from e

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        func_sig: FuncSig = get_func_sig(pait_core_model.func, cache_sig=False)
        for pre_depend in pait_core_model.pre_depend_list:
            depend_func_sig: FuncSig = get_func_sig(pre_depend, cache_sig=False)
            app.check_pre_depend(pait_core_model, depend_func_sig, cls)
        cls.param_field_check_handler(pait_core_model, func_sig.func, func_sig.param_list)

    ####################
    # pre load handler #
    ####################
    @classmethod
    def depend_handler(cls, pait_core_model: "PaitCoreModel", func: CallType) -> resource_parse.PreLoadDc:
        """gen depend's pre-load dataclass"""
        func_sig: FuncSig = get_func_sig(func, cache_sig=False)
        func_class_prd = None
        if inspect.isclass(func):
            func_class_prd = cls.get_param_rule_from_parameter_list(
                pait_core_model,
                func,
                get_parameter_list_from_class(func),
            )
        return resource_parse.PreLoadDc(
            call_handler=func,  # depend func gen pait handler in pre-load
            param=cls.get_param_rule_from_parameter_list(pait_core_model, func_sig.func, func_sig.param_list),
            cbv_param=func_class_prd,
        )

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        super().pre_load_hook(pait_core_model, kwargs)
        func_sig: FuncSig = get_func_sig(pait_core_model.func, cache_sig=False)

        kwargs["_pait_pre_depend_dc"] = [
            cls.depend_handler(pait_core_model, pre_depend) for pre_depend in pait_core_model.pre_depend_list
        ]
        kwargs["_pait_pre_load_dc"] = resource_parse.PreLoadDc(
            call_handler=func_sig.func,
            param=cls.get_param_rule_from_parameter_list(pait_core_model, func_sig.func, func_sig.param_list),
        )
        return kwargs
