from dataclasses import MISSING
from typing import Any, Generic, List, Mapping, Optional, Type

from pait.app.base.adapter.request import BaseRequest, BaseRequestExtend, RequestExtendT, RequestT

__all__ = ["BaseRequest", "RequestT", "RequestExtendT", "BaseAppHelper", "BaseRequestExtend"]


class BaseAppHelper(Generic[RequestT, RequestExtendT]):
    """Provide a unified framework call interface for pait"""

    # The class that defines the request object corresponding to the framework (consistent with Request T)
    CbvType: tuple = (Type,)  # The class that defines the cbv object corresponding to the framework
    app_name: str = "BaseAppHelper"  # Define the name corresponding to the framework

    request_class: Type[BaseRequest[RequestT, RequestExtendT]] = BaseRequest

    def __init__(self, args: List[Any], kwargs: Mapping[str, Any]):
        """
        Extract the required data from the passed parameters,
        such as the self parameter in cvb mode, the request parameter in starletter
        """
        if args and isinstance(args[0], self.CbvType):
            self.cbv_instance: Any = args[0]
        else:
            self.cbv_instance = None

        request: Optional[RequestT] = self._get_request(args)
        if request is None:
            raise ValueError("Unable to get request object")
        self.raw_request: RequestT = request
        self.request: BaseRequest[RequestT, RequestExtendT] = self.request_class(request, args, kwargs)

    def _get_request(self, args: List[Any]) -> Optional[RequestT]:
        for param in args:
            if isinstance(param, self.request_class.RequestType):  # type: ignore
                return param
        return None

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        raise NotImplementedError
