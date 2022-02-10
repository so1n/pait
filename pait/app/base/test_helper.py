import copy
import difflib
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel, ValidationError

from pait.model import response
from pait.model.core import PaitCoreModel
from pait.util import gen_example_dict_from_schema, gen_example_value_from_python, get_pait_response_model

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
        strict_inspection_check_json_content: bool = True,
        find_coro_response_model: bool = False,
        target_pait_response_class: Optional[Type["response.PaitBaseResponseModel"]] = None,
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
        self.strict_inspection_check_json_content: bool = strict_inspection_check_json_content

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

        self.find_coro_response_model: bool = find_coro_response_model
        self.target_pait_response_class: Optional[Type["response.PaitBaseResponseModel"]] = target_pait_response_class
        self._app_init_field()

    def _app_init_field(self) -> None:
        """init request param by application framework"""
        raise NotImplementedError()

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        """load pait dict"""
        raise NotImplementedError()

    @staticmethod
    def _get_status_code(resp: RESP_T) -> int:
        """get response status code"""
        raise NotImplementedError()

    @staticmethod
    def _get_content_type(resp: RESP_T) -> str:
        """get response content type"""
        raise NotImplementedError()

    @staticmethod
    def _get_json(resp: RESP_T) -> dict:
        """get json response"""
        raise NotImplementedError()

    @staticmethod
    def _get_headers(resp: RESP_T) -> Mapping:
        """get response header"""
        raise NotImplementedError()

    @staticmethod
    def _get_text(resp: RESP_T) -> str:
        """get text response"""
        raise NotImplementedError()

    @staticmethod
    def _get_bytes(resp: RESP_T) -> bytes:
        """get bytes response"""
        raise NotImplementedError()

    def _check_diff_resp_dict(
        self, raw_resp: Any, default_resp: Any, parent_key_list: Optional[List[str]] = None
    ) -> bool:
        """check resp data structure diff, Only return True to pass the verification"""
        raw_parent_key_list: List[str] = parent_key_list or []
        try:
            if isinstance(raw_resp, dict):
                for key, value in raw_resp.items():
                    parent_key_list = copy.deepcopy(raw_parent_key_list)
                    parent_key_list.append(key)
                    if not self._check_diff_resp_dict(value, default_resp[key], parent_key_list):
                        return False
                return True
            elif isinstance(raw_resp, list) or isinstance(raw_resp, tuple):
                if (
                    raw_resp
                    and default_resp
                    and not self._check_diff_resp_dict(raw_resp[0], default_resp[0], parent_key_list)
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

        real_response_model: Optional[Type[response.PaitBaseResponseModel]] = None
        max_quick_ratio: float = 0.0
        model_check_msg_dict: Dict[Type[response.PaitBaseResponseModel], List[str]] = {}
        response_model_list: List[Type[response.PaitBaseResponseModel]] = (
            self.pait_core_model.response_model_list
            if not self.find_coro_response_model
            else [
                get_pait_response_model(
                    self.pait_core_model.response_model_list,
                    target_pait_response_class=self.target_pait_response_class,
                    find_core_response_model=self.find_coro_response_model,
                )
            ]
        )
        for response_model in response_model_list:
            error_msg_list: List[str] = []
            if self._get_status_code(resp) not in response_model.status_code:
                error_msg_list.append("check status code error.")
            if response_model.media_type not in self._get_content_type(resp):
                error_msg_list.append("check media type error.")

            resp_header: Mapping = self._get_headers(resp)
            for key, _ in response_model.header.items():
                if key not in resp_header:
                    error_msg_list.append(f"check header error. Can not found header:{key} in {resp_header}")

            # check content
            if issubclass(response_model, response.PaitJsonResponseModel):
                response_data_model: Type[BaseModel] = response_model.response_data
                resp_dict: Optional[dict] = self._get_json(resp)
                if not resp_dict:
                    continue
                response_data_default_dict: dict = gen_example_dict_from_schema(response_data_model.schema())
                ratio: float = difflib.SequenceMatcher(
                    None,
                    str(gen_example_value_from_python(resp_dict)),
                    str(response_data_default_dict),
                ).quick_ratio()
                if ratio > max_quick_ratio:
                    max_quick_ratio = ratio
                    real_response_model = response_model
                try:
                    response_data_model(**resp_dict)
                    if self.strict_inspection_check_json_content and not self._check_diff_resp_dict(
                        resp_dict, response_data_default_dict
                    ):
                        error_msg_list.append("check json structure error")
                except (ValidationError, RuntimeError) as e:
                    error_msg_list.append(f"check json content error, exec: {e}")

            elif issubclass(response_model, response.PaitHtmlResponseModel) or issubclass(
                response_model, response.PaitTextResponseModel
            ):
                real_response_model = response_model
                if not isinstance(self._get_text(resp), type(response_model.response_data)):
                    error_msg_list.append("check text content type error")  # pragma: no cover
            elif issubclass(response_model, response.PaitFileResponseModel):
                real_response_model = response_model
                if not isinstance(self._get_bytes(resp), type(response_model.response_data)):
                    error_msg_list.append("check bytes content type error")  # pragma: no cover
            else:
                raise TypeError(f"Pait not support response model:{response_model}")
            if not error_msg_list:
                return
            else:
                model_check_msg_dict[response_model] = error_msg_list
        response_dict: dict = {
            "status_code": self._get_status_code(resp),
            "media_type": self._get_content_type(resp),
            "headers": self._get_headers(resp),
            "obj": resp,
        }
        if real_response_model in model_check_msg_dict:
            raise RuntimeError(
                f"Check Response Error."
                f" maybe error result: {model_check_msg_dict[real_response_model]}"
                f" by response model:{real_response_model}"
                f" response info: {response_dict}"
            )
        raise RuntimeError(
            "Check Response Error. "
            f"response error result:{model_check_msg_dict} "
            f"total response model:{self.pait_core_model.response_model_list}. "
            f"response info: {response_dict} "
        )  # pragma: no cover

    def _replace_path(self, path_str: str) -> Optional[str]:
        raise NotImplementedError()

    def _real_request(self, method: str) -> RESP_T:
        """Whether the structure of the check response is correct"""
        raise NotImplementedError()

    def request(self, method: Optional[str] = None) -> RESP_T:
        """user call test request api"""
        if not method:
            # auto select method
            if len(self.pait_core_model.method_list) == 1:
                method = self.pait_core_model.method_list[0]
            else:
                raise RuntimeError(
                    f"Pait Can not auto select method, please choice method in {self.pait_core_model.method_list}"
                )
        resp: RESP_T = self._real_request(method)
        if self.pait_core_model.response_model_list:
            self._assert_response(resp)
        return resp

    def json(self, method: Optional[str] = None) -> dict:
        return self._get_json(self.request(method))

    def text(self, method: Optional[str] = None) -> str:
        return self._get_text(self.request(method))

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
