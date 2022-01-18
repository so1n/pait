from typing import Any, Callable, Dict, Optional

from sanic.response import json

from pait.model.response import PaitJsonResponseModel
from pait.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin as _AsyncAutoCompleteJsonRespPlugin

__all__ = ["AsyncAutoCompleteJsonRespPlugin"]


class AsyncAutoCompleteJsonRespPlugin(_AsyncAutoCompleteJsonRespPlugin):
    def __init__(
        self,
        *,
        pait_response_model: PaitJsonResponseModel,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        dumps: Optional[Callable[..., str]] = None,
        **json_kwargs: Any,
    ) -> None:
        super(AsyncAutoCompleteJsonRespPlugin, self).__init__(pait_response_model=pait_response_model)
        self.status: int = status
        self.headers: Optional[Dict[str, str]] = headers
        self.content_type = content_type
        self.dumps: Optional[Callable[..., str]] = dumps
        self.json_kwargs: dict = json_kwargs

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        response_dict: Any = await super(AsyncAutoCompleteJsonRespPlugin, self).__call__(*args, **kwargs)
        return json(
            response_dict,
            status=self.status,
            headers=self.headers,
            content_type=self.content_type,
            dumps=self.dumps,
            **self.json_kwargs,
        )
