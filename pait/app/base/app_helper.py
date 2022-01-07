import logging
from typing import Any, List, Mapping


class BaseAppHelper(object):
    """Provide a unified framework call interface for pait"""

    RequestType = type(None)
    FormType = type(None)
    FileType = type(None)
    HeaderType = type(None)
    app_name: str = "BaseAppHelper"

    def __init__(self, class_: Any, args: List[Any], kwargs: Mapping[str, Any]):
        """
        Extract the required data from the passed parameters,
        such as the self parameter in cvb mode, the request parameter in starletter
        """
        self.cbv_instance: Any = class_

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
                logging.warning("Pait only support self and request args param")
                break
            new_args.append(param)

        self.request: Any = request
        self.request_args: List[Any] = new_args
        self.request_kwargs: Mapping[str, Any] = kwargs

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
