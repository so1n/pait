import copy
import difflib
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, List, Mapping, Optional, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel, ValidationError

from pait import _pydanitc_adapter
from pait.model import response
from pait.util import gen_example_dict_from_schema, gen_example_value_from_python, get_pait_response_model

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

RESP_T = TypeVar("RESP_T")
_error_separator = "\n" + ">" * 20 + "\n"


class CheckResponseException(Exception):
    def __init__(
        self,
        status_code: Optional[int] = None,
        media_type: Optional[str] = None,
        headers: Optional[Mapping] = None,
        resp: Any = None,
        func: Optional[Callable] = None,
        message: Optional[str] = None,
    ):
        self.status_code: Optional[int] = status_code
        self.media_type: Optional[str] = media_type
        self.headers: Optional[Mapping] = headers
        self.resp: Any = resp
        self.func: Optional[Callable] = func
        self.message: Optional[str] = message
        super().__init__(self.message)


class BaseTestHelper(Generic[RESP_T]):
    client: Any

    def __init__(
        self,
        client: Any,
        func: Callable,
        load_app: Optional[Callable] = None,
        pait_dict: Optional[Dict[str, "PaitCoreModel"]] = None,
        body_dict: Optional[dict] = None,
        cookie_dict: Optional[dict] = None,
        file_dict: Optional[dict] = None,
        form_dict: Optional[dict] = None,
        header_dict: Optional[dict] = None,
        path_dict: Optional[dict] = None,
        query_dict: Optional[dict] = None,
        strict_inspection_check_json_content: bool = True,
        enable_assert_response: bool = True,
        target_pait_response_class: Optional[Type["response.BaseResponseModel"]] = None,
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
        self._load_app = load_app or getattr(self, "load_app", None)
        self.client: Any = client
        self.func: Callable = func
        # pait dict handle
        if pait_dict:
            self.pait_dict: Dict[str, "PaitCoreModel"] = pait_dict
        else:
            self.pait_dict = self._gen_pait_dict()
        self.pait_core_model: "PaitCoreModel" = self.pait_dict[pait_id]

        self.body_dict: Optional[dict] = body_dict
        self.cookie_dict: Optional[dict] = cookie_dict
        self.file_dict: Optional[dict] = file_dict
        self.form_dict: Optional[dict] = form_dict
        self.header_dict: dict = header_dict or {}
        self.path_dict: Optional[dict] = path_dict
        self.query_dict: Optional[dict] = query_dict
        self.strict_inspection_check_json_content: bool = strict_inspection_check_json_content
        self.enable_assert_response: bool = enable_assert_response

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

        self.target_pait_response_class: Optional[Type["response.BaseResponseModel"]] = target_pait_response_class
        self._app_init_field()

    def _app_init_field(self) -> None:
        """init request param by application framework"""
        raise NotImplementedError()

    def _gen_pait_dict(self) -> Dict[str, "PaitCoreModel"]:
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

    def _assert_response(self, resp: RESP_T) -> Optional[Exception]:
        """Whether the structure of the check response is correct"""
        if not self.pait_core_model.response_model_list:
            return None

        real_response_model: Optional[Type[response.BaseResponseModel]] = None
        max_quick_ratio: float = 0.0
        model_check_msg_dict: Dict[Type[response.BaseResponseModel], List[str]] = {}
        response_model_list: List[Type[response.BaseResponseModel]] = (
            self.pait_core_model.response_model_list
            if not self.target_pait_response_class
            else [
                get_pait_response_model(
                    self.pait_core_model.response_model_list,
                    target_pait_response_class=self.target_pait_response_class,
                )
            ]
        )
        for response_model in response_model_list:
            error_msg_list: List[str] = []
            status_code: int = self._get_status_code(resp)
            content_type: str = self._get_content_type(resp)
            if status_code not in response_model.status_code:
                error_msg_list.append(
                    "check status code error. "
                    f"Get the response with a status code of {status_code}, "
                    f"but the response_model specifies a status of {response_model.status_code}"
                )

            if response_model.media_type not in content_type:
                error_msg_list.append(
                    "check media type error."
                    f"Get the response with a media type of {content_type}, "
                    f"but the response_model specifies a media type of {response_model.media_type}"
                )

            resp_header: Mapping = self._get_headers(resp)
            for key, _ in response_model.get_header_example_dict().items():
                if key not in resp_header:
                    error_msg_list.append(
                        f"check header error. Can not found header:{key} in {str(resp_header).strip()}"
                    )

            # check content
            if issubclass(response_model, response.JsonResponseModel):
                response_data_model: Type[BaseModel] = response_model.response_data
                if not response_data_model:
                    return None
                resp_dict: Optional[dict] = None
                try:
                    resp_dict = self._get_json(resp)
                except Exception:
                    pass

                if not resp_dict and not isinstance(resp_dict, dict):
                    continue

                response_data_default_dict: dict = gen_example_dict_from_schema(
                    _pydanitc_adapter.model_json_schema(response_data_model)
                )
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
                    # like Basemodel.config.extra = forbid
                    if self.strict_inspection_check_json_content and not self._check_diff_resp_dict(
                        resp_dict, response_data_default_dict
                    ):
                        differ = difflib.Differ()
                        diff_iterator = differ.compare(str(response_data_default_dict), str(resp_dict))
                        diff_content = "\n".join(diff_iterator)
                        error_msg_list.append(f"check json structure error, \n{diff_content}")
                except (ValidationError, RuntimeError) as e:
                    error_msg_list.append(f"check json content error, exec: {e}")

            elif issubclass(response_model, response.HtmlResponseModel) or issubclass(
                response_model, response.TextResponseModel
            ):
                real_response_model = response_model
                if not isinstance(self._get_text(resp), type(response_model.response_data)):
                    error_msg_list.append("check text content type error")  # pragma: no cover
            elif issubclass(response_model, response.FileResponseModel):
                real_response_model = response_model
                if not isinstance(self._get_bytes(resp), type(response_model.response_data)):
                    error_msg_list.append("check bytes content type error")  # pragma: no cover
            else:
                return TypeError(f"Pait not support response model:{response_model}")
            if not error_msg_list:
                return None
            else:
                model_check_msg_dict[response_model] = error_msg_list
        if real_response_model in model_check_msg_dict:
            error_str: str = "\n    ".join(model_check_msg_dict[real_response_model])
            return CheckResponseException(
                status_code=self._get_status_code(resp),
                media_type=self._get_content_type(resp),
                headers=self._get_headers(resp),
                resp=resp,
                func=self.func,
                message=(
                    f"maybe error result: {_error_separator}{error_str}\n"
                    f"{_error_separator}by response model:{real_response_model}\n"
                ),
            )

        error_str = ""
        for k, v in model_check_msg_dict.items():
            error_str += str(k) + ":\n" + "    \n".join(v)
        return CheckResponseException(
            status_code=self._get_status_code(resp),
            media_type=self._get_content_type(resp),
            headers=self._get_headers(resp),
            resp=resp,
            func=self.func,
            message=(
                f"response error result: {_error_separator}{error_str} \n"
                f"{_error_separator}by response model list:{self.pait_core_model.response_model_list}.\n"
            ),
        )

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
        if self.pait_core_model.response_model_list and self.enable_assert_response:
            exc = self._assert_response(resp)
            if exc:
                raise exc
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
