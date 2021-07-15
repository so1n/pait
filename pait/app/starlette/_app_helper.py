from typing import Any, Coroutine, Dict, List, Mapping, Optional, Tuple, Type

from starlette.datastructures import FormData, Headers, UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from pait.app.base import BaseAppHelper
from pait.model.response import PaitResponseModel
from pait.util import LazyProperty, gen_example_json_from_schema

__all__ = ["AppHelper"]


class AppHelper(BaseAppHelper):
    RequestType = Request
    FormType = FormData
    FileType = UploadFile
    HeaderType = Headers
    app_name = "starlette"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)
        self._form: Optional[FormData] = None

    def body(self) -> dict:
        return self.request.json()

    def cookie(self) -> dict:
        return self.request.cookies

    async def get_form(self) -> FormData:
        if self._form:
            return self._form
        form: FormData = await self.request.form()
        self._form = form
        return form

    def file(self) -> Coroutine[Any, Any, FormData]:
        async def _() -> FormData:
            return await self.get_form()

        return _()

    def form(self) -> Coroutine[Any, Any, Dict[str, Any]]:
        @LazyProperty()
        async def _form() -> Dict[str, Any]:
            form_data: FormData = await self.get_form()
            return {key: form_data.getlist(key)[0] for key, _ in form_data.items()}

        return _form()

    def header(self) -> Headers:
        return self.request.headers

    def path(self) -> dict:
        return self.request.path_params

    def query(self) -> dict:
        return dict(self.request.query_params)

    def multiform(self) -> Coroutine[Any, Any, Dict[str, List[Any]]]:
        @LazyProperty()
        async def _multiform() -> Dict[str, List[Any]]:
            form_data: FormData = await self.get_form()
            return {
                key: [i for i in form_data.getlist(key) if not isinstance(i, UploadFile)]
                for key, _ in form_data.items()
            }

        return _multiform()

    @LazyProperty(is_class_func=True)
    def multiquery(self) -> Dict[str, Any]:
        return {key: self.request.query_params.getlist(key) for key, _ in self.request.query_params.items()}

    @staticmethod
    def make_mock_response(pait_response: Type[PaitResponseModel]) -> Response:
        if pait_response.media_type == "application/json" and pait_response.response_data:
            resp: Response = JSONResponse(gen_example_json_from_schema(pait_response.response_data.schema()))
            resp.status_code = pait_response.status_code[0]
            if pait_response.header:
                resp.headers.update(pait_response.header)
            return resp
        else:
            raise NotImplementedError()

