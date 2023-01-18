from typing import Any, Generic, List, Mapping, TypeVar

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


class BaseRequest(Generic[RequestT, RequestExtendT]):
    # The class that defines the request object corresponding to the framework (consistent with Request T)
    RequestType: RequestT = type(None)  # type: ignore
    FormType = type(None)  # The class that defines the form object corresponding to the framework
    FileType = type(None)  # The class that defines the file object corresponding to the framework
    HeaderType = type(None)  # The class that defines the header object corresponding to the framework

    def __init__(self, request: RequestT, args: List[Any], kwargs: Mapping[str, Any]):
        self.request: RequestT = request
        self.args: List[Any] = args
        self.kwargs: Mapping[str, Any] = kwargs
        self.request_kwargs: Mapping[str, Any] = kwargs

    def request_extend(self) -> BaseRequestExtend[RequestT]:
        return BaseRequestExtend(self.request)

    def cookie(self) -> Any:
        raise NotImplementedError

    def header(self) -> Any:
        raise NotImplementedError

    def path(self) -> Any:
        raise NotImplementedError

    def query(self) -> Any:
        raise NotImplementedError

    def json(self) -> dict:
        return self.body()

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
