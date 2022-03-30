import logging
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from pait.core import Pait
from pait.field import Query
from pait.g import config
from pait.model.response import PaitHtmlResponseModel, PaitJsonResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag

logger: logging.Logger = logging.getLogger(__name__)
__all__ = ["DocHtmlRespModel", "OpenAPIRespModel", "AddDocRoute"]


class DocHtmlRespModel(PaitHtmlResponseModel):
    header: dict = {"X-Example-Type": "html"}
    description: str = "doc html response"


class OpenAPIRespModel(PaitJsonResponseModel):
    class OpenAPIResponseModel(BaseModel):
        pass

    description: str = "open api json response"
    # TODO replace to openapi response model
    response_data: dict = {}  # type: ignore


class AddDocRoute(object):
    not_found_exc: Exception

    def __init__(
        self,
        scheme: Optional[str] = None,
        open_json_url_only_path: bool = False,
        prefix: str = "",
        pin_code: str = "",
        title: str = "",
        open_api_tag_list: Optional[List[Dict[str, Any]]] = None,
        project_name: str = "",
    ):
        if pin_code:
            logging.info(f"doc route start pin code:{pin_code}")
        self.scheme: Optional[str] = scheme
        self.open_json_url_only_path: bool = open_json_url_only_path
        self.prefix: str = prefix or "/"
        self.pin_code: str = pin_code
        self.title: str = title or "Pait Doc"
        self.open_api_tag_list: Optional[List[Dict[str, Any]]] = open_api_tag_list
        self.project_name: str = project_name
        self._is_gen: bool = False

    def _get_request_pin_code(self, r_pin_code: str = Query.i("", alias="pin_code")) -> Optional[str]:
        if self.pin_code:
            if r_pin_code != self.pin_code:
                raise self.not_found_exc
        return r_pin_code

    @staticmethod
    def _get_doc_pait(pait_class: Type[Pait]) -> Pait:
        return pait_class(
            author=config.author or ("so1n",),
            status=config.status or PaitStatus.release,
            tag=(Tag("pait_doc", desc="pait default doc route"),),
            group="pait_doc",
        )

    def _gen_route(self, app: Any) -> Any:  # type: ignore
        raise NotImplementedError()

    def gen_route(self, app: Any) -> Any:
        if self._is_gen:
            raise RuntimeError("Doc route has been generated")
        self._gen_route(app)
        self._is_gen = True
