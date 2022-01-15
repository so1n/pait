from typing import Any, Optional

from starlette.responses import JSONResponse

from pait.model.response import PaitJsonResponseModel
from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin as _AsyncAutoCompleteJsonRespPlugin
from pait.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin as _AutoCompleteJsonRespPlugin

__all__ = ["AutoCompleteJsonRespPlugin", "AsyncAutoCompleteJsonRespPlugin"]


class AsyncAutoCompleteJsonRespPlugin(_AsyncAutoCompleteJsonRespPlugin):
    def __init__(
        self,
        *,
        pait_response_model: PaitJsonResponseModel,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
    ) -> None:
        super(AsyncAutoCompleteJsonRespPlugin, self).__init__(pait_response_model=pait_response_model)
        self.status_code: int = status_code
        self.headers: Optional[dict] = headers
        self.media_type: Optional[str] = media_type

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        default_response_dict: dict = self.pait_response_model.get_default_dict()
        response_dict: dict = await self.call_next(*args, **kwargs)
        default_response_dict.update(response_dict)
        return JSONResponse(
            response_dict, status_code=self.status_code, headers=self.headers, media_type=self.media_type
        )


class AutoCompleteJsonRespPlugin(_AutoCompleteJsonRespPlugin):
    def __init__(
        self,
        *,
        pait_response_model: PaitJsonResponseModel,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
    ) -> None:
        super(AutoCompleteJsonRespPlugin, self).__init__(pait_response_model=pait_response_model)
        self.status_code: int = status_code
        self.headers: Optional[dict] = headers
        self.media_type: Optional[str] = media_type

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        default_response_dict: dict = self.pait_response_model.get_default_dict()
        response_dict: dict = self.call_next(*args, **kwargs)
        default_response_dict.update(response_dict)
        return JSONResponse(
            default_response_dict, status_code=self.status_code, headers=self.headers, media_type=self.media_type
        )
