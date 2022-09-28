import logging
from dataclasses import MISSING
from typing import Any, Generic, List, Mapping, Type, TypeVar

RequestT = TypeVar("RequestT")


class BaseRequestExtend(Generic[RequestT]):
    def __init__(self, request: RequestT) -> None:
        self.request: RequestT = request

    @property
    def scheme(self) -> str:
        raise NotImplementedError

    @property
    def path(self) -> str:
        raise NotImplementedError

    @property
    def hostname(self) -> str:
        raise NotImplementedError


RequestExtendT = TypeVar("RequestExtendT", bound=BaseRequestExtend)


class BaseAppHelper(Generic[RequestT, RequestExtendT]):
    """Provide a unified framework call interface for pait"""

    # The class that defines the request object corresponding to the framework (consistent with Request T)
    RequestType = type(None)
    FormType = type(None)  # The class that defines the form object corresponding to the framework
    FileType = type(None)  # The class that defines the file object corresponding to the framework
    HeaderType = type(None)  # The class that defines the header object corresponding to the framework
    CbvType: tuple = (Type,)  # The class that defines the cbv object corresponding to the framework
    app_name: str = "BaseAppHelper"  # Define the name corresponding to the framework

    def __init__(self, args: List[Any], kwargs: Mapping[str, Any]):
        """
        Extract the required data from the passed parameters,
        such as the self parameter in cvb mode, the request parameter in starletter
        """
        if args and isinstance(args[0], self.CbvType):
            self.cbv_instance: Any = args[0]
        else:
            self.cbv_instance = None

        request = None
        new_args: List[Any] = []
        for param in args:
            if type(param) == self.RequestType:
                request = param
                # In cbv, request parameter will only appear after the self parameter
                break
            elif param == self.cbv_instance:
                pass
            else:
                # In cbv, parameter like self, request, {other param}
                # Now, not support other param
                logging.warning(f"Pait only support self and request args param not {param}")
                break
            new_args.append(param)

        # Except for the flask framework, the requests here are all values
        self.request: RequestT = request  # type: ignore
        self.request_args: List[Any] = new_args
        self.request_kwargs: Mapping[str, Any] = kwargs

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        raise NotImplementedError

    def request_extend(self) -> BaseRequestExtend[RequestT]:
        raise NotImplementedError

    def cookie(self) -> Any:
        raise NotImplementedError

    def header(self) -> Any:
        raise NotImplementedError

    def path(self) -> Any:
        raise NotImplementedError

    def query(self) -> Any:
        raise NotImplementedError

    def body(self) -> Any:
        raise NotImplementedError

    def file(self) -> Any:
        raise NotImplementedError

    def form(self) -> Any:
        raise NotImplementedError

    def multiform(self) -> Any:
        raise NotImplementedError

    def multiquery(self) -> Any:
        raise NotImplementedError

    def check_request_type(self, value: Any) -> bool:
        return value is self.RequestType

    def check_file_type(self, value: Any) -> bool:
        return value is self.FileType

    def check_form_type(self, value: Any) -> bool:
        return value is self.FormType

    def check_header_type(self, value: Any) -> bool:
        return value is self.HeaderType
