import sys
from tempfile import NamedTemporaryFile
from typing import IO, TYPE_CHECKING, Any, Dict, Generic, Optional, Type, TypeVar

from typing_extensions import Literal

from pait.model import response
from pait.plugin.base import GetPaitResponseModelFuncType, PluginManager, PrePluginProtocol
from pait.util import get_pait_response_model as _get_pait_response_model

if TYPE_CHECKING:
    from pait.model.context import ContextModel as PluginContext
    from pait.model.core import PaitCoreModel


RESP_T = TypeVar("RESP_T")


class MockPluginProtocol(PrePluginProtocol, Generic[RESP_T]):
    """Automatically return a json response with sample values based on the response object
    Note: the code logic of the routing function will not be executed
    """

    pait_response_model: Type[response.BaseResponseModel]
    example_column_name: Literal["example", "mock"]

    def __call__(self, context: "PluginContext") -> Any:
        if self._is_async_func:
            return self.async_mock_response()
        return self.mock_response()

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        super().pre_check_hook(pait_core_model, kwargs)
        if not pait_core_model.response_model_list:
            raise RuntimeError(f"{pait_core_model.func} can not found response model")
        if "pait_response_model" in kwargs:
            raise RuntimeError("Please use response_model_list param")

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        kwargs = super().pre_load_hook(pait_core_model, kwargs)
        get_pait_response_model = kwargs.get("get_pait_response_model", None)
        if not get_pait_response_model:
            raise RuntimeError("Can not found get_pait_response_model func")
        kwargs["pait_response_model"] = get_pait_response_model(pait_core_model.response_model_list)
        return kwargs

    def get_response(self) -> RESP_T:
        raise NotImplementedError()

    def get_file_response(self, temporary_file: IO[bytes], f: Any) -> RESP_T:
        raise RuntimeError("Not Implemented")  # pragma: no cover

    async def async_get_file_response(self, temporary_file: Any, f: Any) -> RESP_T:
        raise RuntimeError("Not Implemented")  # pragma: no cover

    def set_info_to_response(self, resp: RESP_T) -> None:
        raise NotImplementedError()

    def mock_response(self) -> RESP_T:
        if issubclass(self.pait_response_model, response.FileResponseModel):
            named_temporary_file: IO[bytes] = NamedTemporaryFile()
            f: Any = named_temporary_file.__enter__()
            try:
                resp: RESP_T = self.get_file_response(named_temporary_file, f)
            except Exception as e:
                exc_type, exc_val, exc_tb = sys.exc_info()
                named_temporary_file.__exit__(exc_type, exc_val, exc_tb)
                raise e
            self.set_info_to_response(resp)
        elif not issubclass(self.pait_response_model, response.BaseResponseModel):
            raise NotImplementedError(f"make_mock_response not support {self.pait_response_model}")
        else:
            resp = self.get_response()
        return resp

    async def async_mock_response(self) -> RESP_T:
        if issubclass(self.pait_response_model, response.FileResponseModel):
            import aiofiles  # type: ignore

            tf: aiofiles.tempfile.AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
            f: Any = await tf.__aenter__()
            try:
                resp: RESP_T = await self.async_get_file_response(tf, f)
            except Exception as e:
                exc_type, exc_val, exc_tb = sys.exc_info()
                await tf.__aexit__(exc_type, exc_val, exc_tb)
                raise e
            self.set_info_to_response(resp)
        elif not issubclass(self.pait_response_model, response.BaseResponseModel):
            raise NotImplementedError(f"make_mock_response not support {self.pait_response_model}")
        else:
            resp = self.get_response()
        return resp

    @classmethod
    def build(  # type: ignore
        cls,  # type: ignore
        example_column_name: Literal["example", "mock"] = "example",  # type: ignore
        get_pait_response_model: Optional[GetPaitResponseModelFuncType] = None,  # type: ignore
    ) -> "PluginManager":  # type: ignore
        return super().build(
            example_column_name=example_column_name,
            get_pait_response_model=get_pait_response_model or _get_pait_response_model,
        )
