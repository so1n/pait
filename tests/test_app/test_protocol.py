import importlib
import inspect
import sys

from pait import app as any_app
from pait.app.auto_load_app import app_list

other_app: list = [importlib.import_module(f"pait.app.{i}") for i in app_list]


class TestProtocol:
    @staticmethod
    def _real_check_func_type_hint(
        app_signature: inspect.Signature, any_app_signature: inspect.Signature, app_name: str, func_name: str
    ) -> None:
        assert app_signature.return_annotation == any_app_signature.return_annotation
        if len(app_signature.parameters) != len(any_app_signature.parameters):
            raise ValueError(f"{app_name}' func <{func_name}> param length error")
        for param, param_annotation in any_app_signature.parameters.items():
            if param == "app":
                continue
            try:
                assert app_signature.parameters[param] == param_annotation
            except KeyError as e:
                raise KeyError(f"{app_name}'func <{func_name}> not found key {e}")

    def _check_func_type_hint(self, func_name: str) -> None:
        any_app_signature: inspect.Signature = inspect.signature(getattr(any_app, func_name))
        for app in other_app:
            app_signature: inspect.Signature = inspect.signature(getattr(app, func_name))
            self._real_check_func_type_hint(app_signature, any_app_signature, app.__name__, func_name)

    def _check_func_type_hint_by_other_module(self, module_name: str, func_name: str) -> None:
        for app in other_app:
            # reset import
            self._clean_app_from_sys_module()
            importlib.import_module(app.__name__.split(".")[-1])
            importlib.reload(importlib.import_module(f"pait.app.any.{module_name}"))

            any_app_signature: inspect.Signature = inspect.signature(
                getattr(importlib.import_module(f"pait.app.any.{module_name}"), func_name)
            )
            app_signature: inspect.Signature = inspect.signature(
                getattr(importlib.import_module(f"{app.__name__}.{module_name}"), func_name)
            )
            self._real_check_func_type_hint(app_signature, any_app_signature, app.__name__, func_name)

    @staticmethod
    def _clean_app_from_sys_module() -> None:
        for i in app_list:
            sys.modules.pop(i, None)

    def test_load_app(self) -> None:
        self._check_func_type_hint(any_app.load_app.__name__)

    def test_pait_func(self) -> None:
        self._check_func_type_hint(any_app.pait.__name__)

    def test_pait_class(self) -> None:
        self._check_func_type_hint(any_app.Pait.__name__)  # type: ignore

    def test_add_doc_route(self) -> None:
        self._check_func_type_hint(any_app.add_doc_route.__name__)

    def test_add_doc_route_class(self) -> None:
        self._check_func_type_hint(any_app.AddDocRoute.__name__)  # type: ignore

    def test_grpc_gateway_route(self) -> None:
        self._check_func_type_hint_by_other_module("grpc_route", "GrpcGatewayRoute")

    def test_security_api_key(self) -> None:
        self._check_func_type_hint_by_other_module("security.api_key", "api_key")
