from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from typing_extensions import Self

from pait.core import Pait, PaitCreateSubParamTypedDict, PaitInitParamTypedDict, Unpack, easy_to_develop_merge_kwargs
from pait.types import CallType

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])


def url_join(base_url: str, path: str) -> str:
    if not path or path == "/":
        return base_url
    if base_url.endswith("/") and path.startswith("/"):
        return base_url + path[1:]
    return base_url + path


@dataclass
class RouteDc(object):
    route: CallType
    path: str
    pait_param: PaitInitParamTypedDict
    method_list: List[str]
    framework_extra_param: Dict[str, Any]


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
        self._route: List[RouteDc] = []

    @property
    def _pait_type(self) -> Type[Pait]:
        raise NotImplementedError

    @staticmethod
    def get_openapi_path(path_str: str) -> str:
        raise NotImplementedError

    @property
    def route(self) -> List[RouteDc]:
        return self._route

    def inject(
        self, app: Any, replace_openapi_url_to_url: Optional[Callable[[str], str]] = None, **kwargs: Any
    ) -> None:
        raise NotImplementedError

    def __lshift__(self, other: "BaseAPIRoute") -> Self:
        return self.include_sub_route(other)

    def include_sub_route(self, *api_route: "BaseAPIRoute") -> Self:
        for api_route_item in api_route:
            if not api_route_item.route:
                raise ValueError(f"{api_route} can't be None")
            for route in api_route_item.route:
                route.path = self.url_join(self.path, route.path)
                route.pait_param = easy_to_develop_merge_kwargs(self._pait_kwargs, route.pait_param, "before")
                self.route.append(route)
        return self

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
                pait_param=easy_to_develop_merge_kwargs(self._pait_kwargs, kwargs, "before"),
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
