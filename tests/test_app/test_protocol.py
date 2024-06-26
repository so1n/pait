import importlib
import inspect
import sys

from pait.app import any as any_app
from pait.app.auto_load_app import app_list

other_app: list = [importlib.import_module(f"pait.app.{i}") for i in app_list]


class BaseTestProtocol:
    @staticmethod
    def _real_check_func_type_hint(
        app_signature: inspect.Signature,
        any_app_signature: inspect.Signature,
        app_name: str,
        func_name: str,
        support_extra_param: bool = False,
    ) -> None:
        assert app_signature.return_annotation == any_app_signature.return_annotation
        if not support_extra_param and len(app_signature.parameters) != len(any_app_signature.parameters):
            print(len(app_signature.parameters), len(any_app_signature.parameters))
            raise ValueError(f"{app_name}' func <{func_name}> param length error")
        for param, param_annotation in any_app_signature.parameters.items():
            if param in ("app", "kwargs"):
                continue
            try:
                assert app_signature.parameters[param] == param_annotation
            except KeyError as e:
                raise KeyError(f"{app_name}'func <{func_name}> not found key {e}")

    def _check_func_type_hint(
        self,
        func_name: str,
        support_extra_param: bool = False,
    ) -> None:
        for app in app_list:
            self._clean_app_from_sys_module()
            importlib.import_module(app)

            obj = importlib.import_module(f"pait.app.{app}")
            any_app_signature: inspect.Signature = inspect.signature(getattr(any_app, func_name))
            app_signature: inspect.Signature = inspect.signature(getattr(obj, func_name))
            self._real_check_func_type_hint(
                app_signature, any_app_signature, obj.__name__, func_name, support_extra_param=support_extra_param
            )

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


class TestProtocol(BaseTestProtocol):
    def test_load_app(self) -> None:
        func_name = any_app.load_app.__name__
        for app in app_list:
            self._clean_app_from_sys_module()
            importlib.import_module(app)

            obj = importlib.import_module(f"pait.app.{app}")
            any_app_signature: inspect.Signature = inspect.signature(getattr(any_app, func_name))
            app_signature: inspect.Signature = inspect.signature(getattr(obj, func_name))
            app_signature = inspect.Signature(
                [v for k, v in app_signature.parameters.items() if k != "pait"],
                return_annotation=app_signature.return_annotation,
            )
            self._real_check_func_type_hint(
                app_signature, any_app_signature, obj.__name__, func_name, support_extra_param=False
            )

    def test_pait_func(self) -> None:
        self._check_func_type_hint(any_app.pait.__name__)

    def test_pait_class(self) -> None:
        importlib.reload(importlib.import_module("pait.app.any"))
        importlib.reload(importlib.import_module("pait.app"))
        importlib.reload(any_app)
        importlib.import_module("pait.app.any")
        self._check_func_type_hint(any_app.Pait.__name__)  # type: ignore

    def test_field(self) -> None:
        from pait.field import BaseRequestResourceField

        init_signature: inspect.Signature = inspect.signature(BaseRequestResourceField.__init__)
        ignore_signature: inspect.Signature = inspect.signature(BaseRequestResourceField.i)
        for name, parameters in ignore_signature.parameters.items():
            assert parameters == init_signature.parameters[name]


class TestHttpExceptionProtocol(BaseTestProtocol):
    def test_http_exception(self) -> None:
        self._check_func_type_hint(any_app.http_exception.__name__)


class TestAttributeProtocol(BaseTestProtocol):
    def test_set_app_attribute(self) -> None:
        self._check_func_type_hint(any_app.set_app_attribute.__name__)

    def test_get_app_attribute(self) -> None:
        self._check_func_type_hint(any_app.get_app_attribute.__name__)


class TestSecurityProtocol(BaseTestProtocol):
    def test_security_api_key(self) -> None:
        self._check_func_type_hint_by_other_module("security.api_key", "APIKey")

    def test_security_oauth2(self) -> None:
        self._check_func_type_hint_by_other_module("security.oauth2", "BaseOAuth2PasswordBearer")

    def test_security_http(self) -> None:
        for item in ["HTTPBasic", "HTTPDigest", "HTTPBearer"]:
            self._check_func_type_hint_by_other_module("security.http", item)


class TestSimpleRouteProtocol(BaseTestProtocol):
    def test_add_simple_route(self) -> None:
        self._check_func_type_hint(any_app.add_simple_route.__name__, support_extra_param=True)

    def test_add_multi_simple_route(self) -> None:
        self._check_func_type_hint(any_app.add_multi_simple_route.__name__, support_extra_param=True)


class TestPluginProtocol(BaseTestProtocol):
    def test_plugin_auto_complete_json_resp(self) -> None:
        self._check_func_type_hint_by_other_module("plugin.auto_complete_json_resp", "AutoCompleteJsonRespPlugin")

    def test_plugin_cache_response(self) -> None:
        self._check_func_type_hint_by_other_module("plugin.cache_response", "CacheResponsePlugin")

    def test_plugin_check_json_resp(self) -> None:
        self._check_func_type_hint_by_other_module("plugin.check_json_resp", "CheckJsonRespPlugin")

    def test_plugin_mock_response(self) -> None:
        self._check_func_type_hint_by_other_module("plugin.mock_response", "MockPlugin")

    def test_plugin_unified_response(self) -> None:
        self._check_func_type_hint_by_other_module("plugin.unified_response", "UnifiedResponsePlugin")

    def test_plugin_at_most_one_of(self) -> None:
        self._check_func_type_hint_by_other_module("plugin", "AtMostOneOfPlugin")

    def test_plugin_required(self) -> None:
        self._check_func_type_hint_by_other_module("plugin", "RequiredPlugin")
