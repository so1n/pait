from typing import Any, Dict, List, Mapping, Tuple

from flask import Request, request
from werkzeug.datastructures import EnvironHeaders, ImmutableMultiDict

from pait.app.base import BaseAppHelper
from pait.util import LazyProperty

__all__ = ["AppHelper"]


class AppHelper(BaseAppHelper):
    RequestType = Request
    FormType = ImmutableMultiDict
    FileType = Request.files
    HeaderType = EnvironHeaders
    app_name = "flask"

    def __init__(self, class_: Any, args: Tuple[Any, ...], kwargs: Mapping[str, Any]):
        super().__init__(class_, args, kwargs)

        self.request = request

    def body(self) -> dict:
        return request.json

    def cookie(self) -> dict:
        return request.cookies

    def file(self) -> Request.files:  # type: ignore
        return request.files

    def form(self) -> Request.form:  # type: ignore
        return request.form

    def header(self) -> EnvironHeaders:
        return request.headers

    def path(self) -> Mapping[str, Any]:
        return self.request_kwargs

    def query(self) -> Dict[str, Any]:
        return request.args

    @LazyProperty()
    def multiform(self) -> Dict[str, List[Any]]:
        return {key: request.form.getlist(key) for key, _ in request.form.items()}

    @LazyProperty()
    def multiquery(self) -> Dict[str, List[Any]]:
        return {key: request.args.getlist(key) for key, _ in request.args.items()}
