from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from any_api.openapi.model.util import HttpMethodLiteral
from typing_extensions import Self, get_args

from pait.core import (
    Pait,
    PaitCreateSubParamTypedDict,
    PaitInitParamTypedDict,
    Unpack,
    easy_to_develop_merge_kwargs,
    get_core_model,
)
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
append_pait_param_key_list = [key for key in PaitCreateSubParamTypedDict.__annotations__ if key.startswith("append_")]


def url_join(base_url: str, path: str) -> str:
    if not path or path == "/":
        return base_url
    if base_url.endswith("/") and path.startswith("/"):
        return base_url + path[1:]
    return base_url + path


def merge_pait_param(
    route_pait_param: APIRoutePaitParamTypedDict, api_route_pait_param: APIRoutePaitParamTypedDict
) -> PaitCreateSubParamTypedDict:
    """Merge the new parameter into the existing one
    - If it's an append parameter, then only the content will be appended
    - If the original parameter already exists, it will not be processed
    - The extra parameter appends only the key that does not exist
    """
    append_param: APIRoutePaitParamTypedDict = {}
    for key, value in api_route_pait_param.items():
        if key.startswith("append"):  # type: ignore[literal-required]
            if key in route_pait_param:
                route_pait_param[key] = route_pait_param[key] + value  # type: ignore[literal-required]
            else:
                append_param[key] = value  # type: ignore[literal-required]
        elif route_pait_param.get(key) is None:
            route_pait_param[key] = value  # type: ignore[literal-required]
    if "extra" in api_route_pait_param:
        extra = deepcopy(api_route_pait_param.get("extra", {}))
        extra.update(route_pait_param.get("extra", {}))
        route_pait_param["extra"] = extra
    merged_extra = route_pait_param.get("extra")
    route_pait_param = easy_to_develop_merge_kwargs(route_pait_param, append_param)
    if merged_extra is not None:
        route_pait_param["extra"] = merged_extra  # type: ignore[literal-required]

    return route_pait_param  # type: ignore


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

    def _get_framework_extra_param(self, route_dc: RouteType) -> Dict[str, Any]:
        framework_extra_param = self.framework_extra_param.copy()
        framework_extra_param.update(route_dc.framework_extra_param)
        return framework_extra_param

    def _get_url(self, path: str, replace_openapi_url_to_url: Optional[Callable[[str], str]]) -> str:
        replace_openapi_url_to_url = replace_openapi_url_to_url or self.replace_openapi_url_to_url
        return replace_openapi_url_to_url(path)

    def _gen_route(self, route_dc: RouteDc, pait: Pait) -> CallType:
        route = pait(**route_dc.pait_param)(route_dc.route)
        get_core_model(route).openapi_path = self.get_openapi_path(route_dc.path)
        return route

    def _before_inject(self, app: Any, **kwargs: Any) -> None:
        pass

    def _after_inject(self, app: Any, **kwargs: Any) -> None:
        pass

    def _is_cbv_route(self, route: Type) -> bool:
        raise NotImplementedError

    def _add_api_route(
        self,
        app: Any,
        route: CallType,
        route_dc: RouteDc,
        url: str,
        framework_extra_param: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError

    def _add_cbv_route(
        self,
        app: Any,
        route_dc: CbvRouteDc,
        url: str,
        framework_extra_param: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError

    def inject(
        self, app: Any, replace_openapi_url_to_url: Optional[Callable[[str], str]] = None, **kwargs: Any
    ) -> None:
        """Inject the '_route' into the app"""
        _pait = self._pait_type()
        self._before_inject(app, **kwargs)
        for route_dc in self.route:
            framework_extra_param = self._get_framework_extra_param(route_dc)
            url = self._get_url(route_dc.path, replace_openapi_url_to_url)
            if isinstance(route_dc, RouteDc):
                self._add_api_route(
                    app,
                    self._gen_route(route_dc, _pait),
                    route_dc,
                    url,
                    framework_extra_param,
                    **kwargs,
                )
            elif isinstance(route_dc, CbvRouteDc) and self._is_cbv_route(route_dc.route):
                self._cbv_handler(_pait, route_dc.route, route_dc.pait_param)
                self._add_cbv_route(app, route_dc, url, framework_extra_param, **kwargs)
            else:
                raise ValueError(f"route_dc type error: {route_dc}")
        self._after_inject(app, **kwargs)

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
