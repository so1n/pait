import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import BaseConfig

from pait.app.base import BaseAppHelper
from pait.g import config, pait_data
from pait.model.core import PaitCoreModel
from pait.model.response import PaitBaseResponseModel
from pait.model.status import PaitStatus
from pait.model.util import sync_config_data_to_pait_core_model
from pait.param_handle import AsyncParamHandler, ParamHandler
from pait.util import get_func_sig


class Pait(object):
    app_helper_class: "Type[BaseAppHelper]"
    make_mock_response_fn: staticmethod  # real type hints: Callable[[Type[PaitBaseResponseModel]], Any]]

    def __init__(
        self,
        make_mock_response_fn: Optional[Callable[[Type[PaitBaseResponseModel]], Any]] = None,
        enable_mock_response: bool = False,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        at_most_one_of_list: Optional[List[List[str]]] = None,
        required_by: Optional[Dict[str, List[str]]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
    ):

        check_cls_param_list: List[str] = ["app_helper_class", "make_mock_response_fn"]
        for cls_param in check_cls_param_list:
            if not getattr(self, cls_param, None):
                raise ValueError(
                    f"Please specify the value of the {cls_param} parameter, you can refer to `pait.app.xxx`"
                )
        if not isinstance(self.app_helper_class, type):
            raise TypeError(f"{self.app_helper_class} must be class")
        if not issubclass(self.app_helper_class, BaseAppHelper):
            raise TypeError(f"{self.app_helper_class} must sub from {BaseAppHelper.__class__.__name__}")
        if getattr(self.make_mock_response_fn, "__self__", None):
            raise TypeError(
                "Set error make_mock_response_fn, should use `staticmethod` func. "
                "like `make_mock_response_fn = staticmethod(make_mock_response)`"
            )

        self._make_mock_response_fn: Callable[[Type[PaitBaseResponseModel]], Any] = (
            make_mock_response_fn or self.make_mock_response_fn
        )
        self._enable_mock_response: bool = enable_mock_response
        self._pydantic_model_config: Optional[Type[BaseConfig]] = pydantic_model_config
        # param check
        self._pre_depend_list: Optional[List[Callable]] = pre_depend_list
        self._at_most_one_of_list: Optional[List[List[str]]] = at_most_one_of_list
        self._required_by: Optional[Dict[str, List[str]]] = required_by
        # doc
        self._author: Optional[Tuple[str, ...]] = author
        self._desc: Optional[str] = desc
        self._summary: Optional[str] = summary
        self._name: Optional[str] = name
        self._status: Optional[PaitStatus] = status
        self._group: Optional[str] = group
        self._tag: Optional[Tuple[str, ...]] = tag
        self._response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = response_model_list

    def __call__(
        self,
        make_mock_response_fn: Callable[[Type[PaitBaseResponseModel]], Any] = None,
        enable_mock_response: bool = False,
        pydantic_model_config: Optional[Type[BaseConfig]] = None,
        # param check
        pre_depend_list: Optional[List[Callable]] = None,
        at_most_one_of_list: Optional[List[List[str]]] = None,
        required_by: Optional[Dict[str, List[str]]] = None,
        # doc
        author: Optional[Tuple[str, ...]] = None,
        desc: Optional[str] = None,
        summary: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[PaitStatus] = None,
        group: Optional[str] = None,
        tag: Optional[Tuple[str, ...]] = None,
        response_model_list: Optional[List[Type[PaitBaseResponseModel]]] = None,
    ) -> Callable:
        app_name: str = self.app_helper_class.app_name
        enable_mock_response = enable_mock_response or self._enable_mock_response
        pydantic_model_config = pydantic_model_config or self._pydantic_model_config
        pre_depend_list = pre_depend_list or self._pre_depend_list
        at_most_one_of_list = at_most_one_of_list or self._at_most_one_of_list
        required_by = required_by or self._required_by
        author = author or self._author
        desc = desc or self._desc
        summary = summary or self._summary
        name = name or self._name
        group = group or self._group
        tag = tag or self._tag
        response_model_list = response_model_list or self._response_model_list

        def wrapper(func: Callable) -> Callable:
            # Pre-parsing function signatures
            get_func_sig(func)

            # gen pait core model and register to pait data
            pait_core_model: PaitCoreModel = PaitCoreModel(
                author=author,
                app_helper_class=self.app_helper_class,
                make_mock_response_fn=make_mock_response_fn or self._make_mock_response_fn,
                desc=desc,
                summary=summary,
                func=func,
                func_name=name,
                status=status,
                group=group,
                tag=tag,
                response_model_list=response_model_list,
                pre_depend_list=pre_depend_list,
                pydantic_model_config=pydantic_model_config,
            )
            sync_config_data_to_pait_core_model(config, pait_core_model, enable_mock_response=enable_mock_response)
            pait_data.register(app_name, pait_core_model)

            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    async with AsyncParamHandler(
                        self.app_helper_class,
                        func,
                        pait_core_model.pydantic_model_config,
                        at_most_one_of_list=at_most_one_of_list,
                        pre_depend_list=pre_depend_list,
                        required_by=required_by,
                        args=args,
                        kwargs=kwargs,
                    ) as p:
                        return await pait_core_model.pait_func(*p.args, **p.kwargs)

                return dispatch
            else:

                @wraps(func)
                def dispatch(*args: Any, **kwargs: Any) -> Callable:
                    with ParamHandler(
                        self.app_helper_class,
                        func,
                        pait_core_model.pydantic_model_config,
                        at_most_one_of_list=at_most_one_of_list,
                        pre_depend_list=pre_depend_list,
                        required_by=required_by,
                        args=args,
                        kwargs=kwargs,
                    ) as p:
                        return pait_core_model.pait_func(*p.args, **p.kwargs)

                return dispatch

        return wrapper
