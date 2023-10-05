from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from any_api.openapi.model.util import HttpMethodLiteral
from typing_extensions import Self, get_args

from pait.core import Pait, PaitCreateSubParamTypedDict, PaitInitParamTypedDict, Unpack, get_core_model
from pait.types import CallType

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])

APIRoutePaitParamTypedDict = Union[PaitInitParamTypedDict, PaitCreateSubParamTypedDict]


@dataclass
class CbvRouteDc(object):
    route: Type
    path: str
    pait_param: PaitCreateSubParamTypedDict
    framework_extra_param: Dict[str, Any]


@dataclass
class RouteDc(object):
    route: CallType
    path: str
    pait_param: PaitCreateSubParamTypedDict
    method_list: List[str]
    framework_extra_param: Dict[str, Any]


RouteType = Union[RouteDc, CbvRouteDc]


def url_join(base_url: str, path: str) -> str:
    if not path or path == "/":
        return base_url
    if base_url.endswith("/") and path.startswith("/"):
        return base_url + path[1:]
    return base_url + path


def merge_pait_param(
    base_param: APIRoutePaitParamTypedDict, new_param: APIRoutePaitParamTypedDict
) -> PaitCreateSubParamTypedDict:
    """Merge the new parameter into the existing one
    - If it's an append parameter, then only the content will be appended
    - If the original parameter already exists, it will not be processed
    - The extra parameter appends only the key that does not exist
    """
    for key, value in new_param.items():
        if key.startswith("append") and key in base_param:
            base_param[key] = base_param[key] + value  # type: ignore[literal-required]
        elif base_param.get(key) is None:
            base_param[key] = value  # type: ignore[literal-required]
    if "extra" in new_param:
        extra = deepcopy(new_param.get("extra", {}))
        extra.update(base_param.get("extra", {}))
        base_param["extra"] = extra

    return base_param  # type: ignore


class BaseAPIRoute(object):
    replace_openapi_url_to_url = staticmethod(lambda x: x)
    url_join = staticmethod(url_join)

    def __init__(
        self,
        path: str = "",
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitCreateSubParamTypedDict],
    ) -> None:
        self._pait_kwargs = kwargs
        self.framework_extra_param: Dict[str, Any] = framework_extra_param or {}
        self.path = path
        self._route: List[RouteType] = []

    @property
    def _pait_type(self) -> Type[Pait]:
        """get pait type"""
        raise NotImplementedError

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        """get route openapi path"""
        raise NotImplementedError

    @property
    def route(self) -> List[RouteType]:
        return self._route

    def inject(
        self, app: Any, replace_openapi_url_to_url: Optional[Callable[[str], str]] = None, **kwargs: Any
    ) -> None:
        """Inject the '_route' into the app"""
        raise NotImplementedError

    @staticmethod
    def _cbv_handler(pait: Pait, cbv_class: Type, pait_param: PaitCreateSubParamTypedDict) -> None:
        """Handle CBV routes
        - Prevent users from not using @pait decorators
        - New parameters have been added
        """
        for http_method in get_args(HttpMethodLiteral):
            func = getattr(cbv_class, http_method, None)
            if not func:
                continue
            try:
                get_core_model(func)
            except TypeError:
                setattr(cbv_class, http_method, pait()(func))
        pait.pre_load_cbv(cbv_class, **pait_param)

    def __lshift__(self, other: "BaseAPIRoute") -> Self:
        return self.include_sub_route(other)

    def include_sub_route(self, *api_route: "BaseAPIRoute") -> Self:
        """Loading sub routes"""
        for api_route_item in api_route:
            if not api_route_item.route:
                raise ValueError(f"{api_route} can't be None")
            for route in api_route_item.route:
                route.path = self.url_join(self.path, route.path)
                route.pait_param = merge_pait_param(route.pait_param, self._pait_kwargs)
                self.route.append(route)
        return self

    def add_cbv_route(
        self,
        cbv_clss: Type,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> None:
        _framework_extra_param = self.framework_extra_param.copy()
        _framework_extra_param.update(framework_extra_param or {})
        self._route.append(
            CbvRouteDc(
                route=cbv_clss,
                path=self.url_join(self.path, path),
                pait_param=merge_pait_param(kwargs, self._pait_kwargs),
                framework_extra_param=_framework_extra_param,
            )
        )

    def add_api_route(
        self,
        func: CallType,
        method: List[str],
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> None:
        _framework_extra_param = self.framework_extra_param.copy()
        _framework_extra_param.update(framework_extra_param or {})
        self._route.append(
            RouteDc(
                route=func,
                method_list=method,
                path=url_join(self.path, path),
                pait_param=merge_pait_param(kwargs, self._pait_kwargs),
                framework_extra_param=_framework_extra_param,
            )
        )

    def add_route(
        self,
        method: List[str],
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        def decorator(func: _CallableT) -> _CallableT:
            self.add_api_route(func, method, path, framework_extra_param, **kwargs)
            return func

        return decorator

    def get(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["GET"], path, framework_extra_param, **kwargs)

    def post(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["POST"], path, framework_extra_param, **kwargs)

    def put(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["PUT"], path, framework_extra_param, **kwargs)

    def delete(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["DELETE"], path, framework_extra_param, **kwargs)

    def patch(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["PATCH"], path, framework_extra_param, **kwargs)

    def head(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["HEAD"], path, framework_extra_param, **kwargs)

    def options(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["OPTIONS"], path, framework_extra_param, **kwargs)

    def trace(
        self,
        path: str,
        framework_extra_param: Optional[Dict[str, Any]] = None,
        **kwargs: Unpack[PaitInitParamTypedDict],
    ) -> Callable[[_CallableT], _CallableT]:
        return self.add_route(["TRACE"], path, framework_extra_param, **kwargs)
