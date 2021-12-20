import copy
import difflib
import inspect
import logging
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, Tuple, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel, ValidationError

from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel
from pait.util import gen_example_dict_from_schema, gen_example_json_from_python


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
        """
        :param client:  test client
        :param func:  route handle decorated by pait
        :param pait_dict:  pait core data
        :param body_dict:  request body param
        :param cookie_dict:  request cookie param
        :param file_dict:  request file param
        :param form_dict:  request form param
        :param header_dict:  request herder param
        :param path_dict:  request path param
        :param query_dict:  request query param
        """
        pait_id: str = getattr(func, "_pait_id", "")
        if not pait_id:
            raise RuntimeError(f"Can not found pait id from {func}")

        self.client: Any = client
        self.func: Callable = func
        # pait dict handle
        if pait_dict:
            self.pait_dict: Dict[str, PaitCoreModel] = pait_dict
        else:
            self.pait_dict = self._gen_pait_dict()
        self.pait_core_model: PaitCoreModel = self.pait_dict[pait_id]

        self.body_dict: Optional[dict] = body_dict
        self.cookie_dict: Optional[dict] = cookie_dict
        self.file_dict: Optional[dict] = file_dict
        self.form_dict: Optional[dict] = form_dict
        self.header_dict: dict = header_dict or {}
        self.path_dict: Optional[dict] = path_dict
        self.query_dict: Optional[dict] = query_dict

        # path handle
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

        # add query path by path
        if self.query_dict:
            self.path = self.path + "?" + urlencode(self.query_dict, True)
        if not self.path.startswith("/"):
            self.path = "/" + self.path

        # auto select method
        self.method: Optional[str] = None
        if len(self.pait_core_model.method_list) == 1:
            self.method = self.pait_core_model.method_list[0]
        elif "GET" in self.pait_core_model.method_list:
            self.method = "GET"
        elif "POST" in self.pait_core_model.method_list:
            self.method = "POST"

        self._app_init_field()

    def _app_init_field(self) -> None:
        """init request param by application framework"""
        raise NotImplementedError()

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        """load pait dict"""
        raise NotImplementedError()

    @staticmethod
    def _check_resp_status(resp: RESP_T, response_model: Type[PaitResponseModel]) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _check_resp_media_type(resp: RESP_T, response_model: Type[PaitResponseModel]) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _get_json(resp: RESP_T) -> dict:
        raise NotImplementedError()

    def _diff_resp_dict(self, raw_resp: Any, default_resp: Any, parent_key_list: Optional[List[str]] = None) -> bool:
        """check resp data structure diff"""
        raw_parent_key_list: List[str] = parent_key_list or []
        try:
            if isinstance(raw_resp, dict):
                for key, value in raw_resp.items():
                    parent_key_list = copy.deepcopy(raw_parent_key_list)
                    parent_key_list.append(key)
                    if not self._diff_resp_dict(value, default_resp[key], parent_key_list):
                        return False
                return True
            elif isinstance(raw_resp, list) or isinstance(raw_resp, tuple):
                if (
                    raw_resp
                    and default_resp
                    and not self._diff_resp_dict(raw_resp[0], default_resp[0], parent_key_list)
                ):
                    return False
                return True
            else:
                return True
        except KeyError:
            raise RuntimeError(f"Can not found key from model, key:{' -> '.join(parent_key_list or '')}")

    def _assert_response(self, resp: RESP_T) -> None:
        """Whether the structure of the check response is correct"""
        if not self.pait_core_model.response_model_list:
            return

        json_error_response_dict: Dict[Type[BaseModel], Tuple[Exception, float]] = {}
        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                self._check_resp_status(resp, response_model),
                self._check_resp_media_type(resp, response_model),
            ]
            if response_model.media_type == "application/json":
                response_data_model: Any = response_model.response_data
                if response_data_model:
                    if not (inspect.isclass(response_data_model) and issubclass(response_data_model, BaseModel)):
                        raise TypeError(f"{response_data_model} not issubclass {BaseModel}")
                    resp_dict: Optional[dict] = self._get_json(resp)
                    if not resp_dict:
                        check_list.append(True)
                        continue
                    response_data_default_dict: dict = gen_example_dict_from_schema(response_data_model.schema())
                    try:
                        response_data_model(**resp_dict)
                        check_list.append(self._diff_resp_dict(resp_dict, response_data_default_dict))
                    except (ValidationError, RuntimeError) as e:
                        check_list.append(False)
                        json_error_response_dict[response_data_model] = (
                            e,
                            difflib.SequenceMatcher(
                                None,
                                str(gen_example_json_from_python(resp_dict.copy())),
                                str(response_data_default_dict),
                            ).quick_ratio(),
                        )
            if all(check_list):
                return
        if json_error_response_dict:
            exc: Optional[Exception] = None
            model: Optional[Type[BaseModel]] = None
            max_quick_ratio: float = 0.0
            for _model, response_error in json_error_response_dict.items():
                if response_error[1] > max_quick_ratio:
                    max_quick_ratio = response_error[1]
                    exc = response_error[0]
                    model = _model
            if exc:
                raise RuntimeError(f"maybe error:{exc} by response_model: {model}") from exc
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}.")

    def _replace_path(self, path_str: str) -> Optional[str]:
        raise NotImplementedError()

    def _make_response(self, method: str) -> RESP_T:
        """Whether the structure of the check response is correct"""
        raise NotImplementedError()

    def request(self, method: Optional[str] = None) -> RESP_T:
        """user call test request api"""
        if not method:
            method = self.method
        if not method:
            raise ValueError("Method is Null")
        resp: RESP_T = self._make_response(method)
        if self.pait_core_model.response_model_list:
            self._assert_response(resp)
        return resp

    def get(self) -> RESP_T:
        return self.request("GET")

    def patch(self) -> RESP_T:
        return self.request("PATCH")

    def post(self) -> RESP_T:
        return self.request("POST")

    def head(self) -> RESP_T:
        return self.request("HEAD")

    def put(self) -> RESP_T:
        return self.request("PUT")

    def delete(self) -> RESP_T:
        return self.request("DELETE")

    def options(self) -> RESP_T:
        return self.request("OPTIONS")
