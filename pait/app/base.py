import logging
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, Tuple, Type, TypeVar
from urllib.parse import urlencode

from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel


class BaseAppHelper(object):
    """Provide a unified framework call interface for pait"""

    RequestType = type(None)
    FormType = type(None)
    FileType = type(None)
    HeaderType = type(None)
    app_name: str = "BaseAppHelper"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        """
        Extract the required data from the passed parameters,
        such as the self parameter in cvb mode, the request parameter in starletter
        """
        self.cbv_class: Any = None

        request = None
        new_args: List[Any] = []
        for param in args:
            if type(param) == self.RequestType:
                request = param
                # In cbv, request parameter will only appear after the self parameter
                break
            elif isinstance(param, class_):
                self.cbv_class = param
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

    @staticmethod
    def make_mock_response(pait_response: Type[PaitResponseModel]) -> Any:
        raise NotImplementedError


RESP_T = TypeVar("RESP_T")


class BaseTestHelper(Generic[RESP_T]):
    client: Any

    def __init__(
        self,
        client: Any,
        func: Callable,
        pait_dict: Optional[Dict[str, PaitCoreModel]] = None,
        body_dict: Optional[dict] = None,
        cookie_dict: Optional[dict] = None,
        file_dict: Optional[dict] = None,
        form_dict: Optional[dict] = None,
        header_dict: Optional[dict] = None,
        path_dict: Optional[dict] = None,
        query_dict: Optional[dict] = None,
    ):
        pait_id: str = getattr(func, "_pait_id", "")
        if not pait_id:
            raise RuntimeError(f"Can not found pait id from {func}")
        self.client: Any = client
        self.func: Callable = func
        if pait_dict:
            self.pait_dict: Dict[str, PaitCoreModel] = pait_dict
        else:
            self.pait_dict = self._gen_pait_dict()

        self.body_dict: Optional[dict] = body_dict
        self.cookie_dict: Optional[dict] = cookie_dict
        self.file_dict: Optional[dict] = file_dict
        self.form_dict: Optional[dict] = form_dict
        self.header_dict: Optional[dict] = header_dict
        self.path_dict: Optional[dict] = path_dict
        self.query_dict: Optional[dict] = query_dict

        self.pait_core_model: PaitCoreModel = self.pait_dict[pait_id]
        self.path: str = self.pait_core_model.path
        if self.path_dict:
            path_list: List[str] = self.path.split("/")
            new_path_list: List[str] = []
            for sub_path in path_list:
                if not sub_path:
                    continue
                new_sub_path: Optional[str] = self._replace_path(sub_path)
                if new_sub_path:
                    new_path_list.append(new_sub_path)
                else:
                    new_path_list.append(sub_path)
            self.path = "/".join([str(i) for i in new_path_list])

        if self.query_dict:
            self.path = self.path + "?" + urlencode(self.query_dict, True)
        if self.file_dict:
            if self.form_dict:
                self.form_dict.update(self.file_dict)
            else:
                self.form_dict = self.file_dict

        self.method: Optional[str] = None
        if len(self.pait_core_model.method_list) == 1:
            self.method = self.pait_core_model.method_list[0]
        elif "GET" in self.pait_core_model.method_list:
            self.method = "GET"
        elif "POST" in self.pait_core_model.method_list:
            self.method = "POST"

        self._app_init_field()

    def _app_init_field(self) -> None:
        raise NotImplementedError()

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        raise NotImplementedError()

    def _assert_response(self, resp: RESP_T) -> None:
        raise NotImplementedError()

    def _replace_path(self, path_str: str) -> Optional[str]:
        raise NotImplementedError()

    def _make_response(self, method: str) -> RESP_T:
        raise NotImplementedError()

    def make_response(self, method: Optional[str] = None) -> RESP_T:
        if not method:
            method = self.method
        if not method:
            raise ValueError("Method is Null")
        resp = self._make_response(method)
        if self.pait_core_model.response_model_list:
            self._assert_response(resp)
        return resp

    def get(self) -> RESP_T:
        return self.make_response("GET")

    def patch(self) -> RESP_T:
        return self.make_response("PATCH")

    def post(self) -> RESP_T:
        return self.make_response("POST")

    def head(self) -> RESP_T:
        return self.make_response("HEAD")

    def put(self) -> RESP_T:
        return self.make_response("PUT")

    def delete(self) -> RESP_T:
        return self.make_response("DELETE")

    def options(self) -> RESP_T:
        return self.make_response("OPTIONS")
