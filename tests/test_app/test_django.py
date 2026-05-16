# flake8: noqa: E402
import importlib
import json
import random
import sys
import types
from contextlib import contextmanager
from functools import partial
from typing import Any, Callable, Generator, List, Optional, Type
from unittest import mock

import pytest
from pytest_mock import MockFixture

django = pytest.importorskip("django")

from django.conf import settings

if not settings.configured:
    settings.configure(
        ALLOWED_HOSTS=["testserver"],
        DEFAULT_CHARSET="utf-8",
        DEBUG=True,
        MIDDLEWARE=["example.django_example.utils.ApiExceptionMiddleware"],
        ROOT_URLCONF="tests.test_app.test_django_urlconf",
        SECRET_KEY="pait-test",
    )
else:
    middleware_list = list(getattr(settings, "MIDDLEWARE", []))
    if "example.django_example.utils.ApiExceptionMiddleware" not in middleware_list:
        settings.MIDDLEWARE = middleware_list + ["example.django_example.utils.ApiExceptionMiddleware"]
    settings.ROOT_URLCONF = "tests.test_app.test_django_urlconf"
django.setup()

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import Client, RequestFactory
from django.urls import clear_url_caches, include, path
from django.views.decorators.http import require_http_methods
from pydantic import BaseModel, Field, ValidationError

from example.django_example import main_example
from pait.app import auto_load_app
from pait.app.any import get_app_attribute, set_app_attribute
from pait.app.base.simple_route import SimpleRoute
from pait.app.django import TestHelper as _TestHelper
from pait.app.django import add_multi_simple_route, add_simple_route, load_app, pait
from pait.app.django.adapter.exception import DjangoHTTPException, http_exception
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.field import Header, Json, Path, Query
from pait.model import response
from pait.model.context import ContextModel
from pait.openapi.doc_route import default_doc_fn_dict
from pait.openapi.openapi import OpenAPI
from tests.conftest import enable_plugin
from tests.test_app.base_api_test import BaseTest
from tests.test_app.base_doc_example_test import BaseTestDocExample
from tests.test_app.base_mcp_test import DjangoMCPHTTPClient, assert_mcp_route, assert_mcp_route_with_custom_path

_TestHelper: Type[_TestHelper] = partial(  # type: ignore
    _TestHelper,
    load_app=partial(load_app, overwrite_already_exists_data=True),
)


class UserModel(BaseModel):
    name: str
    age: int


@pait()
def get_user_route(
    request: HttpRequest,
    uid: int = Path.i(),
    user_name: str = Query.i(alias="user_name"),
) -> JsonResponse:
    return JsonResponse({"uid": uid, "user_name": user_name, "path": request.path})


@pait()
def upsert_user_route(
    user: UserModel = Json.i(raw_return=True),
    request_id: str = Header.i(alias="X-Request-Id"),
) -> JsonResponse:
    return JsonResponse({"user": user.dict(), "request_id": request_id})


@pait()
def raise_http_exception_route() -> JsonResponse:
    raise http_exception(status_code=401, message="Not authenticated", headers={"WWW-Authenticate": "Bearer"})


@require_http_methods(["POST", "PATCH"])
@pait()
def require_http_methods_route() -> JsonResponse:
    return JsonResponse({"ok": True})


setattr(upsert_user_route, "_pait_method_set", {"POST"})
urlpatterns = [
    path("api/user/<int:uid>", get_user_route, name="get_user"),
    path("api/user", upsert_user_route, name="upsert_user"),
    path("api/raise-http-exception", raise_http_exception_route, name="raise_http_exception"),
    path("api/require-http-methods", require_http_methods_route, name="require_http_methods"),
]

urlconf_module = types.ModuleType("tests.test_app.test_django_urlconf")
setattr(urlconf_module, "urlpatterns", urlpatterns)
sys.modules[urlconf_module.__name__] = urlconf_module


def use_urlconf(urlconf: str) -> None:
    settings.ROOT_URLCONF = urlconf
    clear_url_caches()


@contextmanager
def client_ctx(client: Optional[Client] = None) -> Generator[Client, None, None]:
    use_urlconf("example.django_example.main_example")
    main_example.load_example_app()
    yield client or Client()


def _http_exception_response(exc: DjangoHTTPException) -> HttpResponse:
    resp = HttpResponse(str(exc), status=exc.status_code)
    for key, value in exc.headers.items():
        resp.headers[key] = value
    return resp


class DocsTextExceptionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, DjangoHTTPException):
            return _http_exception_response(exc)
        return HttpResponse(str(exc))


class DocsDataExceptionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, DjangoHTTPException):
            return _http_exception_response(exc)
        if isinstance(exc, ValidationError):
            return JsonResponse({"data": exc.errors()})
        return JsonResponse({"data": str(exc)})


class DocsDataStrExceptionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, DjangoHTTPException):
            return _http_exception_response(exc)
        return JsonResponse({"data": str(exc)})


class DocsTipExceptionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        if isinstance(exc, TipException):
            exc = exc.exc
        if isinstance(exc, PaitBaseParamException):
            return JsonResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
        if isinstance(exc, ValidationError):
            error_param_list: list = []
            for item in exc.errors():
                error_param_list.extend(item["loc"])
            return JsonResponse({"code": -1, "msg": f"check error param: {error_param_list}"})
        if isinstance(exc, PaitBaseException):
            return JsonResponse({"code": -1, "msg": str(exc)})
        if isinstance(exc, DjangoHTTPException):
            return _http_exception_response(exc)
        return JsonResponse({"code": -1, "msg": str(exc)})


@contextmanager
def docs_client_ctx(urlpatterns: List[Any], exception_mode: str = "data") -> Generator[Client, None, None]:
    old_urlconf = settings.ROOT_URLCONF
    old_middleware = settings.MIDDLEWARE
    middleware_dict = {
        "data": "tests.test_app.test_django.DocsDataExceptionMiddleware",
        "data_str": "tests.test_app.test_django.DocsDataStrExceptionMiddleware",
        "text": "tests.test_app.test_django.DocsTextExceptionMiddleware",
        "tip": "tests.test_app.test_django.DocsTipExceptionMiddleware",
    }
    module_name = f"tests.test_app.test_django_docs_urlconf_{id(urlpatterns)}"
    urlconf_module = types.ModuleType(module_name)
    setattr(urlconf_module, "urlpatterns", urlpatterns)
    sys.modules[module_name] = urlconf_module
    settings.ROOT_URLCONF = module_name
    settings.MIDDLEWARE = [middleware_dict[exception_mode]]
    clear_url_caches()
    load_app(urlpatterns, overwrite_already_exists_data=True)
    try:
        yield Client()
    finally:
        settings.ROOT_URLCONF = old_urlconf
        settings.MIDDLEWARE = old_middleware
        clear_url_caches()
        sys.modules.pop(module_name, None)


@pytest.fixture
def client() -> Generator[Client, None, None]:
    with client_ctx() as client:
        yield client


@pytest.fixture
def base_test() -> Generator[BaseTest, None, None]:
    with client_ctx() as client:
        yield BaseTest(client, _TestHelper)


def response_test_helper(
    client: Client, route_handler: Callable, pait_response: Type[response.BaseResponseModel]
) -> None:
    from pait.app.django.plugin.mock_response import MockPlugin

    test_helper: _TestHelper = _TestHelper(client, route_handler)
    test_helper.get()

    with enable_plugin(route_handler, MockPlugin.build()):
        resp: HttpResponse = test_helper.get()
        for key, value in pait_response.get_header_example_dict().items():
            assert resp.headers[key] == value
        if issubclass(pait_response, response.HtmlResponseModel) or issubclass(
            pait_response, response.TextResponseModel
        ):
            assert resp.content.decode() == pait_response.get_example_value()
        else:
            try:
                content = resp.content
            except AttributeError:
                content = b"".join(resp.streaming_content)
            assert content == pait_response.get_example_value()


class TestDjango:
    def test_request_response_and_load_app(self) -> None:
        use_urlconf("tests.test_app.test_django_urlconf")
        pait_dict = load_app(urlpatterns, overwrite_already_exists_data=True)
        assert len(pait_dict) >= 4
        assert {pait_model.openapi_path for pait_model in pait_dict.values()} >= {
            "/api/user/{uid}",
            "/api/user",
            "/api/raise-http-exception",
            "/api/require-http-methods",
        }
        require_http_methods_core_model = next(
            pait_model for pait_model in pait_dict.values() if pait_model.path == "api/require-http-methods"
        )
        assert set(require_http_methods_core_model.method_list) == {"POST", "PATCH"}

        client = Client()
        assert client.get("/api/user/1?user_name=so1n").json() == {
            "uid": 1,
            "user_name": "so1n",
            "path": "/api/user/1",
        }
        assert client.post(
            "/api/user",
            data=json.dumps({"name": "appl", "age": 2}),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-1",
        ).json() == {"user": {"name": "appl", "age": 2}, "request_id": "req-1"}
        resp = client.get("/api/raise-http-exception")
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.content.decode() == "Not authenticated"

    def test_post(self, client: Client) -> None:
        test_helper: _TestHelper = _TestHelper(
            client,
            main_example.post_route,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        for resp in [
            test_helper.json(),
            client.post(
                "/api/field/post",
                data=json.dumps({"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}),
                content_type="application/json",
                HTTP_USER_AGENT="customer_agent",
            ).json(),
        ]:
            assert resp["code"] == 0
            assert resp["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/json",
                "sex": "man",
            }

    def test_check_json_route(self, client: Client) -> None:
        for url, api_code in [
            (
                "/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10",
                -1,
            ),
            ("/api/plugin/check-json-plugin?uid=123&user_name=appl&sex=man&age=10&display_age=1", 0),
        ]:
            resp: dict = client.get(url).json()
            assert resp["code"] == api_code
            if api_code == -1:
                assert resp["msg"] == "miss param: ['data', 'age']"

    def test_text_response(self, client: Client) -> None:
        response_test_helper(client, main_example.text_response_route, response.TextResponseModel)

    def test_html_response(self, client: Client) -> None:
        response_test_helper(client, main_example.html_response_route, response.HtmlResponseModel)

    def test_file_response(self, client: Client) -> None:
        response_test_helper(client, main_example.file_response_route, response.FileResponseModel)

    def test_raise_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_tip_route, mocker=mocker)

    def test_raise_not_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.raise_not_tip_route, mocker=mocker, is_raise=False)

    def test_new_raise_not_tip_route(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.raise_tip_route(main_example.new_raise_not_tip_route, mocker=mocker, is_raise=False)

    def test_test_helper_not_support_mutil_method(self, client: Client) -> None:
        method_list = ["GET", "POST"]
        route = require_http_methods(method_list)(main_example.text_response_route)
        setattr(route, "_pait_method_set", method_list)
        old_len = len(main_example.urlpatterns)
        main_example.urlpatterns.append(path("api/new-text-resp", route, name="new_text_resp"))
        try:
            with pytest.raises(RuntimeError) as exc_info:
                _TestHelper(client, main_example.text_response_route).request()
            assert str(exc_info.value) == "Pait Can not auto select method, please choice method in ['GET', 'POST']"
        finally:
            del main_example.urlpatterns[old_len:]

    def test_doc_route(self, client: Client) -> None:
        old_len = len(main_example.urlpatterns)
        try:
            main_example.add_api_doc_route()
            for doc_route_path, fn in default_doc_fn_dict.items():
                resp = client.get(f"/{doc_route_path}?pin-code=6666")
                assert resp.status_code == 200
                assert resp.content.decode() == fn(
                    f"http://testserver/openapi.json?pin-code=6666", title="Pait Api Doc(private)"
                )

            openapi_data = json.loads(client.get("/openapi.json?pin-code=6666&template-token=xxx").content.decode())
            assert "/api/field/post" in openapi_data["paths"]
            assert "/api/security/api-header-key" in openapi_data["paths"]
            resp = client.get(f"/{next(iter(default_doc_fn_dict))}")
            assert resp.status_code == 404
        finally:
            del main_example.urlpatterns[old_len:]

    def test_mcp_route(self, client: Client) -> None:
        assert_mcp_route(DjangoMCPHTTPClient(client), "django-example")

    def test_mcp_route_with_custom_path(self) -> None:
        from example.django_example.mcp_route import (
            add_mcp_demo_route,
            mcp_depend_route,
            mcp_http_dispatcher_route,
            mcp_private_route,
            mcp_response_route,
            mcp_upsert_user_route,
            mcp_user_route,
            mcp_user_summary_route,
        )
        from example.django_example.utils import configure_urlpatterns, route_path

        old_urlconf = settings.ROOT_URLCONF
        app = [
            route_path("api/mcp/user/<int:uid>", mcp_user_route, ["GET"], name="custom_mcp_user"),
            route_path(
                "api/mcp/user-summary/<int:uid>",
                mcp_user_summary_route,
                ["GET"],
                name="custom_mcp_user_summary",
            ),
            route_path("api/mcp/user", mcp_upsert_user_route, ["POST"], name="custom_mcp_upsert_user"),
            route_path("api/mcp/response", mcp_response_route, ["GET"], name="custom_mcp_response"),
            route_path(
                "api/mcp/http-dispatcher",
                mcp_http_dispatcher_route,
                ["GET"],
                name="custom_mcp_http_dispatcher",
            ),
            route_path("api/mcp/depend", mcp_depend_route, ["GET"], name="custom_mcp_depend"),
            route_path("api/mcp/private", mcp_private_route, ["GET"], name="custom_mcp_private"),
        ]
        add_mcp_demo_route(app, mcp_path="/custom-mcp")
        configure_urlpatterns(app, "tests.test_app.test_django_custom_mcp_urlconf")

        try:
            custom_client = Client()
            assert_mcp_route_with_custom_path(DjangoMCPHTTPClient(custom_client, path="/custom-mcp"), "django-example")
        finally:
            use_urlconf(old_urlconf)

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import django as django_module

        with mock.patch.dict("sys.modules", sys.modules):
            assert django_module == auto_load_app.auto_load_app_class()

    def test_app_attribute(self, client: Client) -> None:
        key = "test_app_attribute"
        value = random.randint(1, 100)
        set_app_attribute(main_example.urlpatterns, key, value)

        @pait()
        def demo_route() -> JsonResponse:
            assert get_app_attribute(main_example.urlpatterns, key) == value
            return JsonResponse({})

        old_len = len(main_example.urlpatterns)
        try:
            main_example.urlpatterns.append(path("api/test-invoke-demo", demo_route, name="test_invoke_demo"))
            assert client.get("/api/test-invoke-demo").json() == {}
        finally:
            del main_example.urlpatterns[old_len:]

    def test_load_app_by_include_route(self) -> None:
        @pait()
        def demo(a: int = Query.i()) -> JsonResponse:
            return JsonResponse({"a": a})

        demo_urlpatterns = [path("demo", demo, name="include_demo")]
        app = [path("api/demo/mount/", include(demo_urlpatterns))]
        key = "tests.test_app.test_django_TestDjango.test_load_app_by_include_route.<locals>.demo"

        load_result = load_app(app, overwrite_already_exists_data=True)
        assert key in load_result
        assert load_result[key].path == "api/demo/mount/demo"
        assert load_result[key].openapi_path == "/api/demo/mount/demo"

    def test_auto_complete_json_route(self, base_test: BaseTest) -> None:
        base_test.auto_complete_json_route(main_example.auto_complete_json_route)

    def test_same_alias_name(self, base_test: BaseTest) -> None:
        base_test.same_alias_name(main_example.same_alias_route)

    def test_field_default_factory_route(self, base_test: BaseTest) -> None:
        base_test.field_default_factory_route(main_example.field_default_factory_route)

    def test_pait_base_field_route(self, base_test: BaseTest) -> None:
        base_test.pait_base_field_route(main_example.pait_base_field_route)

    def test_param_at_most_one_of_route(self, base_test: BaseTest) -> None:
        base_test.param_at_most_one_of_route(main_example.param_at_most_onf_of_route_by_extra_param)
        base_test.param_at_most_one_of_route(main_example.param_at_most_onf_of_route)

    def test_param_required_route(self, base_test: BaseTest) -> None:
        base_test.param_required_route(main_example.param_required_route_by_extra_param)
        base_test.param_required_route(main_example.param_required_route)

    def test_check_response(self, base_test: BaseTest) -> None:
        base_test.check_response(main_example.check_response_route)

    def test_mock_route(self, base_test: BaseTest) -> None:
        base_test.mock_route(main_example.mock_route)

    def test_pait_model(self, base_test: BaseTest) -> None:
        base_test.pait_model(main_example.pait_model_route)

    def test_depend_route(self, base_test: BaseTest) -> None:
        base_test.depend_route(main_example.depend_route)

    def test_pre_depend_route(self, base_test: BaseTest) -> None:
        base_test.pre_depend_route(main_example.pre_depend_route)

    def test_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.depend_contextmanager(main_example.depend_contextmanager_route, mocker)

    def test_pre_depend_contextmanager(self, base_test: BaseTest, mocker: MockFixture) -> None:
        base_test.pre_depend_contextmanager(main_example.pre_depend_contextmanager_route, mocker)

    def test_file_route(self, base_test: BaseTest) -> None:
        base_test.file_route(main_example.stream_for_data_route, ignore_path=True)
        base_test.file_route(main_example.multipart_route, ignore_path=True)

    def test_api_key_route(self, base_test: BaseTest) -> None:
        base_test.api_key_route(main_example.api_key_cookie_route, {"cookie_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_header_route, {"header_dict": {"token": "my-token"}})
        base_test.api_key_route(main_example.api_key_query_route, {"query_dict": {"token": "my-token"}})

    def test_get_user_name_by_http_bearer(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_bearer(main_example.get_user_name_by_http_bearer)

    def test_get_user_name_by_http_digest(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_digest(main_example.get_user_name_by_http_digest)

    def test_get_user_name_by_http_basic_credentials(self, base_test: BaseTest) -> None:
        base_test.get_user_name_by_http_basic_credentials(main_example.get_user_name_by_http_basic_credentials)

    def test_oauth2_password_route(self, base_test: BaseTest) -> None:
        base_test.oauth2_password_route(
            login_route=main_example.oauth2_login,
            user_name_route=main_example.oauth2_user_name,
            user_info_route=main_example.oauth2_user_info,
        )

    def test_get_cbv(self, base_test: BaseTest) -> None:
        base_test.get_cbv(main_example.CbvRoute.get)

    def test_post_cbv(self, base_test: BaseTest) -> None:
        base_test.post_cbv(main_example.CbvRoute.post)

    def test_cache_response(self, base_test: BaseTest) -> None:
        from example.django_example.plugin_route import CacheResponsePlugin, Redis

        CacheResponsePlugin.set_redis_to_app(main_example.urlpatterns, Redis(decode_responses=True))
        base_test.cache_response(main_example.cache_response, main_example.cache_response1, app="django")

    def test_cache_other_response_type(self, base_test: BaseTest) -> None:
        from example.django_example.plugin_route import CacheResponsePlugin, Redis

        CacheResponsePlugin.set_redis_to_app(main_example.urlpatterns, Redis(decode_responses=True))
        base_test.cache_other_response_type(
            main_example.text_response_route, main_example.html_response_route, CacheResponsePlugin
        )

    def test_cache_response_param_name(self, base_test: BaseTest) -> None:
        from example.django_example.plugin_route import CacheResponsePlugin, Redis

        base_test.cache_response_param_name(main_example.post_route, CacheResponsePlugin, Redis(decode_responses=True))

    def test_unified_response(self, base_test: BaseTest) -> None:
        base_test.unified_json_response(main_example.unified_json_response)
        base_test.unified_text_response(main_example.unified_text_response)
        base_test.unified_html_response(main_example.unified_html_response)

    def test_check_json_resp_plugin(self, pait_context: ContextModel) -> None:
        from pait.app.django.plugin.check_json_resp import CheckJsonRespPlugin

        assert CheckJsonRespPlugin.get_json(JsonResponse({"demo": 1}), pait_context) == {"demo": 1}

        with pytest.raises(TypeError):
            CheckJsonRespPlugin.get_json(object, pait_context)

        with pytest.raises(TypeError):
            CheckJsonRespPlugin.get_json(HttpResponse(), pait_context)

    def test_gen_response(self) -> None:
        from pait.app.django.adapter.response import gen_response, gen_unifiled_response

        for gen_method in (gen_response, gen_unifiled_response):
            result = gen_method(JsonResponse({"demo": 1}), response_model_class=response.BaseResponseModel)
            assert json.loads(result.content.decode()) == {"demo": 1}

            result = gen_method({"demo": 1}, response_model_class=response.JsonResponseModel)
            assert json.loads(result.content.decode()) == {"demo": 1}

            class HeaderModel(BaseModel):
                demo: str = Field(alias="x-demo", example="123")  # type: ignore[call-arg]

            class MyHtmlResponseModel(response.HtmlResponseModel):
                media_type = "application/demo"
                header = HeaderModel
                status_code = (400,)

            result = gen_method("demo", response_model_class=MyHtmlResponseModel)
            assert result.content == b"demo"
            assert result.headers["Content-Type"] == "application/demo"
            assert result.headers["x-demo"] == "123"
            assert result.status_code == 400

    def test_request_extend(self) -> None:
        from pait.app.django.adapter.request import RequestExtend

        request = RequestFactory().get("/api/demo?a=123", HTTP_HOST="testserver")
        request_extend = RequestExtend(request)
        assert request_extend.scheme == "http"
        assert request_extend.path == "/api/demo"
        assert request_extend.hostname == "testserver"

    def test_openapi_content(self) -> None:
        openapi_content = json.loads(OpenAPI(main_example.urlpatterns).content())
        assert "/api/field/post" in openapi_content["paths"]
        assert "/api/security/api-header-key" in openapi_content["paths"]
        assert "/api/mcp/user/{uid}" in openapi_content["paths"]
        assert openapi_content["paths"]["/api/field/post"]["post"]["tags"] == ["field", "user", "post"]

    def test_simple_route(self, client: Client) -> None:
        def simple_route_factory(num: int) -> Callable:
            @pait(response_model_list=[response.HtmlResponseModel])
            def simple_route() -> str:
                return f"I'm simple route {num}"

            simple_route.__name__ = simple_route.__name__ + str(num)
            return simple_route

        add_simple_route(
            main_example.urlpatterns,
            SimpleRoute(methods=["GET"], url="/api/demo/simple-route-1", route=simple_route_factory(1)),
        )
        add_multi_simple_route(
            main_example.urlpatterns,
            SimpleRoute(methods=["GET"], url="/demo/simple-route-2", route=simple_route_factory(2)),
            SimpleRoute(methods=["GET"], url="/demo/simple-route-3", route=simple_route_factory(3)),
            prefix="/api",
            title="test",
        )
        assert client.get("/api/demo/simple-route-1").content.decode() == "I'm simple route 1"
        assert client.get("/api/demo/simple-route-2").content.decode() == "I'm simple route 2"
        assert client.get("/api/demo/simple-route-3").content.decode() == "I'm simple route 3"

    def test_any_type_route(self, base_test: BaseTest) -> None:
        base_test.any_type(main_example.any_type_route)

    def test_tag_route(self, base_test: BaseTest) -> None:
        base_test.tag(main_example.tag_route)

    def test_api_route(self, base_test: BaseTest) -> None:
        from example.django_example.api_route import APIRouteCBV, get_user_info, health, login

        base_test.api_route_health(health)
        base_test.api_route_get_user_info(get_user_info)
        base_test.api_route_login(login)
        base_test.api_route_cbv(APIRouteCBV)

    def test_example_modules_are_runnable(self) -> None:
        module_name_list = [
            "api_route",
            "depend_route",
            "field_route",
            "file_route",
            "mcp_route",
            "plugin_route",
            "response_route",
            "security_route",
            "main_example",
        ]

        for module_name in module_name_list:
            module = importlib.import_module(f"example.django_example.{module_name}")
            module_urlpatterns = getattr(module, "urlpatterns")
            assert module_urlpatterns
            assert load_app(module_urlpatterns, overwrite_already_exists_data=True)


class TestDjangoDocExample:
    def test_raw_hello_world_demo(self) -> None:
        from docs_source_code.introduction import django_hello_world_demo

        with docs_client_ctx(django_hello_world_demo.urlpatterns) as client:
            resp = client.post(
                "/api",
                data=json.dumps({"uid": 123, "username": "appl"}),
                content_type="application/json",
            )
            assert resp.json() == {"uid": 123, "user_name": "appl"}

    def test_hello_world_demo(self) -> None:
        from docs_source_code.introduction import django_demo

        with docs_client_ctx(django_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(django_demo.demo_post)

    def test_pait_hello_world_demo(self) -> None:
        from docs_source_code.introduction import django_pait_hello_world_demo

        with docs_client_ctx(django_pait_hello_world_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).hello_world_demo(django_pait_hello_world_demo.demo_post)

    def test_how_to_use_field_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_demo

        with docs_client_ctx(django_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_demo(django_demo.demo_route)

    def test_how_to_use_field_with_default_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_default_demo

        with docs_client_ctx(django_with_default_demo.urlpatterns, exception_mode="text") as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_demo(
                django_with_default_demo.demo,
                django_with_default_demo.demo1,
            )

    def test_how_to_use_field_with_default_factory_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_default_factory_demo

        with docs_client_ctx(django_with_default_factory_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_default_factory_demo(
                django_with_default_factory_demo.demo,
                django_with_default_factory_demo.demo1,
            )

    def test_how_to_use_field_with_alias_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_alias_demo

        with docs_client_ctx(django_with_alias_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_alias_demo(django_with_alias_demo.demo)

    def test_how_to_use_field_with_number_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_num_check_demo

        with docs_client_ctx(django_with_num_check_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_number_verify_demo(
                django_with_num_check_demo.demo
            )

    def test_how_to_use_field_with_sequence_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_item_check_demo

        with docs_client_ctx(django_with_item_check_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_sequence_verify_demo(
                django_with_item_check_demo.demo
            )

    def test_how_to_use_field_with_str_verify_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_string_check_demo

        with docs_client_ctx(django_with_string_check_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_str_verify_demo(
                django_with_string_check_demo.demo
            )

    def test_how_to_use_field_with_raw_return_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_raw_return_demo

        with docs_client_ctx(django_with_raw_return_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_raw_return_demo(
                django_with_raw_return_demo.demo
            )

    def test_how_to_use_field_with_custom_not_found_exc_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_field import django_with_not_found_exc_demo

        with docs_client_ctx(django_with_not_found_exc_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_field_with_custom_not_found_exc_demo(
                django_with_not_found_exc_demo.demo
            )

    def test_how_to_use_type_with_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import django_with_model_demo

        with docs_client_ctx(django_with_model_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pydantic_basemodel(
                django_with_model_demo.demo,
                django_with_model_demo.demo1,
            )

    def test_how_to_use_type_with_pait_model_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import django_with_pait_model_demo

        with docs_client_ctx(django_with_pait_model_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_pait_basemodel(
                django_with_pait_model_demo.demo,
                django_with_pait_model_demo.demo1,
            )

    def test_how_to_use_type_with_request_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import django_with_request_demo

        with docs_client_ctx(django_with_request_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_request(django_with_request_demo.demo)

    def test_how_to_use_type_with_unix_datetime_demo(self) -> None:
        from docs_source_code.introduction.how_to_use_type import django_with_unix_datetime_demo

        with docs_client_ctx(django_with_unix_datetime_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).how_to_use_type_with_type_is_customer(
                django_with_unix_datetime_demo.demo
            )

    def test_streaming_file_multipart_demo(self) -> None:
        from docs_source_code.streaming_files import django_multipart_demo

        with docs_client_ctx(django_multipart_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).django_streaming_file_multipart_demo()

    def test_streaming_file_sfd_demo(self) -> None:
        from docs_source_code.streaming_files import django_sfd_demo

        with docs_client_ctx(django_sfd_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).django_streaming_file_sfd_demo()

    def test_streaming_file_secure_upload_demo(self) -> None:
        from docs_source_code.streaming_files import django_secure_upload_demo

        with docs_client_ctx(django_secure_upload_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).django_streaming_file_secure_upload_demo()

    def test_streaming_file_upload_progress_demo(self) -> None:
        from docs_source_code.streaming_files import django_upload_progress_demo

        with docs_client_ctx(django_upload_progress_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).django_streaming_file_upload_progress_demo()

    def test_depend_with_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import django_with_depend_demo

        with docs_client_ctx(django_with_depend_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).with_depend(django_with_depend_demo.demo)

    def test_depend_with_nested_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import django_with_nested_depend_demo

        with docs_client_ctx(django_with_nested_depend_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).with_nested_depend(django_with_nested_depend_demo.demo)

    def test_depend_with_context_manager_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import django_with_context_manager_depend_demo

        with docs_client_ctx(django_with_context_manager_depend_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).with_context_manager_depend(
                django_with_context_manager_depend_demo.demo
            )

    def test_depend_with_class_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import django_with_class_depend_demo

        with docs_client_ctx(django_with_class_depend_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).with_class_depend(django_with_class_depend_demo.demo)

    def test_depend_with_pre_depend_demo(self) -> None:
        from docs_source_code.introduction.depend import django_with_pre_depend_demo

        with docs_client_ctx(django_with_pre_depend_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).with_pre_depend(django_with_pre_depend_demo.demo)

    def test_exception_with_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import django_with_exception_demo

        with docs_client_ctx(django_with_exception_demo.urlpatterns, exception_mode="tip") as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(django_with_exception_demo.demo)

    def test_exception_with_not_use_exception_tip(self) -> None:
        from docs_source_code.introduction.exception import django_with_not_tip_exception_demo

        with docs_client_ctx(django_with_not_tip_exception_demo.urlpatterns, exception_mode="tip") as client:
            BaseTestDocExample(client, _TestHelper).with_exception_tip(django_with_not_tip_exception_demo.demo)

    def test_api_route_basic_demo(self) -> None:
        from docs_source_code.api_route import django_basic_demo

        with docs_client_ctx(django_basic_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_basic_demo(
                django_basic_demo.get_users,
                django_basic_demo.create_user,
                django_basic_demo.get_user,
            )

    def test_api_route_dynamic_route_demo(self) -> None:
        from docs_source_code.api_route import django_dynamic_route_demo

        with docs_client_ctx(django_dynamic_route_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_dynamic_route_demo(django_dynamic_route_demo.greet)

    def test_api_route_advanced_demo(self) -> None:
        from docs_source_code.api_route import django_advanced_demo

        with docs_client_ctx(django_advanced_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_advanced_demo(
                django_advanced_demo.get_profile,
                django_advanced_demo.login,
                django_advanced_demo.OrderAPIView.get,
            )

    def test_api_route_cbv_demo(self) -> None:
        from docs_source_code.api_route import django_cbv_demo

        with docs_client_ctx(django_cbv_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_cbv_demo(django_cbv_demo.UserAPIView)

    def test_api_route_config_inherit_demo(self) -> None:
        from docs_source_code.api_route import django_config_inherit_demo

        with docs_client_ctx(django_config_inherit_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_config_inherit_demo(
                django_config_inherit_demo.get_profile
            )

    def test_api_route_framework_extra_demo(self) -> None:
        from docs_source_code.api_route import django_framework_extra_demo

        with docs_client_ctx(django_framework_extra_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).api_route_framework_extra_demo(django_framework_extra_demo.health)

    def test_openapi_security_with_api_key(self) -> None:
        from docs_source_code.openapi.security import django_with_apikey_demo

        with docs_client_ctx(django_with_apikey_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_api_key(
                django_with_apikey_demo.api_key_cookie_route,
                django_with_apikey_demo.api_key_header_route,
                django_with_apikey_demo.api_key_query_route,
            )

    def test_openapi_security_with_http(self) -> None:
        from docs_source_code.openapi.security import django_with_http_demo

        with docs_client_ctx(django_with_http_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_http(
                django_with_http_demo.get_user_name_by_http_basic_credentials,
                django_with_http_demo.get_user_name_by_http_bearer,
                django_with_http_demo.get_user_name_by_http_digest,
            )

    def test_openapi_security_with_oauth2(self) -> None:
        from docs_source_code.openapi.security import django_with_oauth2_demo

        with docs_client_ctx(django_with_oauth2_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).openapi_security_with_oauth2(
                django_with_oauth2_demo.oauth2_login,
                django_with_oauth2_demo.oauth2_user_info,
                django_with_oauth2_demo.oauth2_user_name,
            )

    def test_mcp_demo(self) -> None:
        from docs_source_code.mcp import django_mcp_demo

        with docs_client_ctx(django_mcp_demo.urlpatterns) as client:
            mcp_client = DjangoMCPHTTPClient(client)
            tool_dict = {tool["name"]: tool for tool in mcp_client.list_tools()["tools"]}
            assert set(tool_dict) == {"get_user", "create_user"}
            assert tool_dict["get_user"]["annotations"] == {"readOnlyHint": True}
            resp = mcp_client.call_tool("get_user", {"path": {"uid": 1}})
            assert resp["isError"] is False
            assert json.loads(resp["content"][0]["text"]) == {"uid": 1, "name": "so1n"}

    def test_simple_route_demo(self) -> None:
        from docs_source_code.other import django_with_simple_route_demo

        with docs_client_ctx(django_with_simple_route_demo.urlpatterns) as client:
            assert client.get("/api/json").json() == {"name": "json"}
            assert client.get("/api/text").content.decode() == "text"
            assert client.get("/api/html").content.decode() == "<h1>html</h1>"

    def test_plugin_with_required_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            django_with_required_plugin_and_extra_param_demo,
            django_with_required_plugin_and_group_extra_param_demo,
            django_with_required_plugin_demo,
        )

        with docs_client_ctx(django_with_required_plugin_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(django_with_required_plugin_demo.demo)
        with docs_client_ctx(django_with_required_plugin_and_group_extra_param_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                django_with_required_plugin_and_group_extra_param_demo.demo
            )
        with docs_client_ctx(django_with_required_plugin_and_extra_param_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_required_plugin(
                django_with_required_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_at_most_of_plugin(self) -> None:
        from docs_source_code.plugin.param_plugin import (
            django_with_at_most_one_of_plugin_and_extra_param_demo,
            django_with_at_most_one_of_plugin_demo,
        )

        with docs_client_ctx(django_with_at_most_one_of_plugin_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                django_with_at_most_one_of_plugin_demo.demo
            )
        with docs_client_ctx(django_with_at_most_one_of_plugin_and_extra_param_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_at_most_one_of_plugin(
                django_with_at_most_one_of_plugin_and_extra_param_demo.demo
            )

    def test_plugin_with_check_json_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import django_with_check_json_plugin_demo

        with docs_client_ctx(django_with_check_json_plugin_demo.urlpatterns, exception_mode="data_str") as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_check_json_response_plugin(
                django_with_check_json_plugin_demo.demo
            )

    def test_plugin_with_auto_complete_response_plugin(self) -> None:
        from docs_source_code.plugin.json_plugin import django_with_auto_complete_json_plugin_demo

        with docs_client_ctx(django_with_auto_complete_json_plugin_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_auto_complete_json_response_plugin(
                django_with_auto_complete_json_plugin_demo.demo
            )

    def test_plugin_with_mock_plugin(self) -> None:
        from docs_source_code.plugin.mock_plugin import django_with_mock_plugin_demo

        with docs_client_ctx(django_with_mock_plugin_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_mock_plugin(django_with_mock_plugin_demo.demo)

    def test_plugin_with_cache_plugin(self) -> None:
        from docs_source_code.plugin.cache_plugin import django_with_cache_plugin_demo

        with docs_client_ctx(django_with_cache_plugin_demo.urlpatterns) as client:
            BaseTestDocExample(client, _TestHelper).plugin_with_cache_plugin(django_with_cache_plugin_demo.demo)

    def test_test_helper_demo(self) -> None:
        from docs_source_code.unit_test_helper import django_test_helper_demo

        old_urlconf = settings.ROOT_URLCONF
        try:
            django_test_helper_demo.test_demo_route()
        finally:
            settings.ROOT_URLCONF = old_urlconf
            clear_url_caches()
