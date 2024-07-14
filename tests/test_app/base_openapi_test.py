from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from any_api.openapi import BaseResponseModel
from any_api.openapi.model.openapi import (
    ApiKeySecurityModel,
    HttpSecurityModel,
    Oauth2SecurityModel,
    OAuthFlowModel,
    OAuthFlowsModel,
    ResponseModel,
)

from example.common import response_model
from pait import _pydanitc_adapter
from pait.app.base.security.oauth2 import OAuth2PasswordRequestFrom
from pait.model.response import create_json_response_model
from pait.openapi.openapi import OpenAPI

if TYPE_CHECKING:
    from any_api.openapi.model.util import HttpMethodLiteral  # isort:skip


class BasicTestOpenAPI(object):
    def __init__(self, app: Any):
        self.app = app
        self.pait_openapi: OpenAPI = OpenAPI(app)

    def _test_success_response_and_fail_response(
        self, response_dict: Dict[str, ResponseModel], success_resp_model: Type[BaseResponseModel]
    ) -> None:
        assert response_dict["200"].description == "success response"
        resp_schema_dict: dict = response_dict["200"].content["application/json"].schema_["oneOf"]

        success_resp_model_key: str = resp_schema_dict[0]["$ref"].split("/")[-1]
        fail_resp_model_key: str = resp_schema_dict[1]["$ref"].split("/")[-1]
        self._test_nested_model(
            self.pait_openapi.model.components["schemas"][success_resp_model_key],
            _pydanitc_adapter.model_json_schema(success_resp_model.response_data),
            _pydanitc_adapter.model_json_schema(success_resp_model.response_data),
        )

        assert self.pait_openapi.model.components["schemas"][
            fail_resp_model_key
        ] == _pydanitc_adapter.model_json_schema(response_model.FailRespModel.response_data)

    def _test_simple_response_and_fail_response(self, response_dict: Dict[str, ResponseModel]) -> None:
        self._test_success_response_and_fail_response(response_dict, response_model.SimpleRespModel)

    def _test_nested_model(self, openapi_schema: dict, pydantic_schema: dict, raw_pydantic_schema: dict) -> None:
        for k, v in openapi_schema.items():
            if isinstance(v, str) and v.startswith("#/components"):
                openapi_k = v.split("/")[-1]
                pydantic_k = pydantic_schema[k].split("/")[-1]
                self._test_nested_model(
                    self.pait_openapi.model.components["schemas"][openapi_k],
                    raw_pydantic_schema["$defs"][pydantic_k],
                    raw_pydantic_schema,
                )
            elif k == "allOf":
                openapi_k = v[0]["$ref"].split("/")[-1]
                pydantic_k = pydantic_schema[k][0]["$ref"].split("/")[-1]
                self._test_nested_model(
                    self.pait_openapi.model.components["schemas"][openapi_k],
                    raw_pydantic_schema["$defs"][pydantic_k],
                    raw_pydantic_schema,
                )
            elif isinstance(v, dict):
                self._test_nested_model(v, pydantic_schema[k], raw_pydantic_schema)
            else:
                assert v == pydantic_schema[k]


class _TestDependOpenAPI(BasicTestOpenAPI):
    def test_depend_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/depend/depend")
        assert route_dict["post"].description == "Testing depend and using request parameters"
        assert any([i in route_dict["post"].operation_id for i in ["depend_route", "DependHandler.post"]])
        assert route_dict["post"].tags == ["depend", "user"]

        assert route_dict["post"].pait_info["group"] == "depend"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "release"  # type: ignore
        assert "depend" in route_dict["post"].pait_info["pait_id"]  # type: ignore

        assert route_dict["post"].parameters[0].name == "user-agent"
        assert route_dict["post"].parameters[0].description == "user agent"
        assert route_dict["post"].parameters[0].in_ == "header"
        assert route_dict["post"].parameters[0].required
        assert route_dict["post"].parameters[0].schema_ == {"type": "string"}

        assert route_dict["post"].parameters[1].name == "user_name"
        assert route_dict["post"].parameters[1].in_ == "query"
        assert route_dict["post"].parameters[1].required
        assert route_dict["post"].parameters[1].schema_ == {"type": "string"}

        assert route_dict["post"].parameters[2].name == "uid"
        assert route_dict["post"].parameters[2].in_ == "query"
        assert route_dict["post"].parameters[2].required
        assert route_dict["post"].parameters[2].schema_ == {"type": "integer"}

        rb_schema_key: str = route_dict["post"].request_body.content["application/json"].schema_["$ref"]
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]
        assert rb_schema["required"] == ["age"]
        assert rb_schema["properties"] == {
            "age": {
                "title": "Age",
                "description": "age",
                "exclusiveMinimum": 1,
                "exclusiveMaximum": 100,
                "type": "integer",
            }
        }
        self._test_simple_response_and_fail_response(route_dict["post"].responses)

    def test_depend_contextmanager_route(self) -> None:
        for path in ["/api/depend/depend-contextmanager", "/api/depend/depend-async-contextmanager"]:
            if path not in self.pait_openapi.model.paths:
                continue
            route_dict = self.pait_openapi.model.paths.pop(path)
            assert any(
                [
                    i in route_dict["get"].operation_id
                    for i in [
                        "depend_contextmanager_route",
                        "depend_async_contextmanager_route",
                        "DependContextmanagerHanler.get",
                        "DependAsyncContextmanagerHanler.get",
                    ]
                ]
            )
            assert route_dict["get"].tags == ["depend"]

            assert route_dict["get"].pait_info["group"] == "depend"  # type: ignore
            assert route_dict["get"].pait_info["status"] == "test"  # type: ignore
            assert any(
                [
                    i in route_dict["get"].pait_info["pait_id"]
                    for i in [
                        "depend_contextmanager_route",
                        "depend_async_contextmanager_route",
                        "DependContextmanagerHanler.get",
                        "DependAsyncContextmanagerHanler.get",
                    ]
                ]
            )

            assert route_dict["get"].parameters[0].description == "user id"
            assert route_dict["get"].parameters[0].in_ == "query"
            assert route_dict["get"].parameters[0].name == "uid"
            assert route_dict["get"].parameters[0].required
            assert route_dict["get"].parameters[0].schema_ == {
                "exclusiveMaximum": 1000,
                "exclusiveMinimum": 10,
                "type": "integer",
            }

            assert route_dict["get"].parameters[1].in_ == "query"
            assert route_dict["get"].parameters[1].name == "is_raise"
            assert route_dict["get"].parameters[1].schema_ == {"default": False, "type": "boolean"}
            self._test_simple_response_and_fail_response(route_dict["get"].responses)

    def test_pre_depend_contextmanager_route(self) -> None:
        for path in ["/api/depend/pre-depend-contextmanager", "/api/depend/pre-depend-async-contextmanager"]:
            if path not in self.pait_openapi.model.paths:
                continue
            route_dict = self.pait_openapi.model.paths.pop(path)
            assert any(
                [
                    i in route_dict["get"].operation_id
                    for i in [
                        "pre_depend_contextmanager_route",
                        "pre_depend_async_contextmanager_route",
                        "PreDependContextmanagerHanler.get",
                        "PreDependAsyncContextmanagerHanler.get",
                    ]
                ]
            )
            assert route_dict["get"].tags == ["depend"]

            assert route_dict["get"].pait_info["group"] == "depend"  # type: ignore
            assert route_dict["get"].pait_info["status"] == "test"  # type: ignore
            assert any(
                [
                    i in route_dict["get"].pait_info["pait_id"]
                    for i in [
                        "pre_depend_contextmanager_route",
                        "pre_depend_async_contextmanager_route",
                        "PreDependContextmanagerHanler.get",
                        "PreDependAsyncContextmanagerHanler.get",
                    ]
                ]
            )

            assert route_dict["get"].parameters[0].description == "user id"
            assert route_dict["get"].parameters[0].in_ == "query"
            assert route_dict["get"].parameters[0].name == "uid"
            assert route_dict["get"].parameters[0].required
            assert route_dict["get"].parameters[0].schema_ == {
                "exclusiveMaximum": 1000,
                "exclusiveMinimum": 10,
                "type": "integer",
            }

            assert route_dict["get"].parameters[1].in_ == "query"
            assert route_dict["get"].parameters[1].name == "is_raise"
            assert route_dict["get"].parameters[1].schema_ == {"default": False, "type": "boolean"}

            self._test_simple_response_and_fail_response(route_dict["get"].responses)


class _TestFieldOpenAPI(BasicTestOpenAPI):
    def test_post_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/field/post")
        assert any([i in route_dict["post"].operation_id for i in ["post_route", "PostHandler.post"]])
        assert route_dict["post"].description == "Test Method:Post Pydantic Model"
        assert route_dict["post"].tags == ["field", "user", "post"]

        assert route_dict["post"].pait_info["group"] == "field"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "release"  # type: ignore
        assert any([i in route_dict["post"].pait_info["pait_id"] for i in ["field_route_post", "PostHandler.post"]])

        assert route_dict["post"].parameters[0].description == "Content-Type"
        assert route_dict["post"].parameters[0].in_ == "header"
        assert route_dict["post"].parameters[0].name == "Content-Type"
        assert route_dict["post"].parameters[0].required
        assert route_dict["post"].parameters[0].schema_ == {"type": "string"}

        rb_schema_key: str = route_dict["post"].request_body.content["application/json"].schema_["$ref"]
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]
        assert rb_schema["required"] == ["uid", "user_name", "age", "sex"]
        assert rb_schema["properties"] == {
            "uid": {
                "title": "Uid",
                "description": "user id",
                "exclusiveMinimum": 10,
                "exclusiveMaximum": 1000,
                "example": "123",
                "type": "integer",
            },
            "user_name": {
                "title": "User Name",
                "description": "user name",
                "maxLength": 4,
                "minLength": 2,
                "example": "so1n",
                "type": "string",
            },
            "age": {
                "title": "Age",
                "description": "age",
                "exclusiveMinimum": 1,
                "exclusiveMaximum": 100,
                "example": 25,
                "type": "integer",
            },
            "sex": {"description": "sex", "allOf": [{"$ref": "#/components/schemas/SexEnum"}]},
        }
        self._test_success_response_and_fail_response(
            route_dict["post"].responses, create_json_response_model(response_model.UserSuccessRespModel)
        )

    def test_same_alias_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/field/same-alias")

        assert any([i in route_dict["get"].operation_id for i in ["same_alias_route", "SameAliasHandler.get"]])
        assert route_dict["get"].description == (
            "Test different request types, but they have the same alias and different parameter names"
        )
        assert route_dict["get"].tags == ["same alias"]

        assert route_dict["get"].pait_info["group"] == "field"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "release"  # type: ignore

        assert any([i in route_dict["get"].pait_info["pait_id"] for i in ["same_alias_route", "SameAliasHandler.get"]])

        assert route_dict["get"].parameters[0].in_ == "header"
        assert route_dict["get"].parameters[0].name == "token"
        assert route_dict["get"].parameters[0].schema_ == {"default": "", "type": "string"}

        assert route_dict["get"].parameters[1].in_ == "query"
        assert route_dict["get"].parameters[1].name == "token"
        assert route_dict["get"].parameters[1].schema_ == {"default": "", "type": "string"}

        self._test_simple_response_and_fail_response(route_dict["get"].responses)

    def test_field_default_factory_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/field/field-default-factory")

        assert any(
            [
                i in route_dict["post"].operation_id
                for i in ["field_default_factory_route", "FieldDefaultFactoryHandler.post"]
            ]
        )
        assert route_dict["post"].tags == ["field"]

        rb_schema_key: str = route_dict["post"].request_body.content["application/json"].schema_["$ref"]
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]

        assert rb_schema["required"] == ["demo_value"]
        assert rb_schema["properties"] == {
            "demo_value": {"title": "Demo Value", "description": "Json body value not empty", "type": "integer"},
            "data_list": {
                "title": "Data List",
                "description": "test default factory",
                "type": "array",
                "items": {"type": "string"},
            },
            "data_dict": {"title": "Data Dict", "description": "test default factory", "type": "object"},
        }

        self._test_simple_response_and_fail_response(route_dict["post"].responses)

    def test_pait_base_field_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/field/pait-base-field/{age}")

        assert any(
            [i in route_dict["post"].operation_id for i in ["pait_base_field_route", "PaitBaseFieldHandler.post"]]
        )
        assert route_dict["post"].tags == ["field"]

        assert route_dict["post"].pait_info["group"] == "field"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "release"  # type: ignore

        assert any(
            [
                i in route_dict["post"].pait_info["pait_id"]
                for i in ["pait_base_field_route", "PaitBaseFieldHandler.post"]
            ]
        )

        assert route_dict["post"].parameters[0].description.startswith("cookie")
        assert route_dict["post"].parameters[0].description == (
            "cookie \n"
            ">Note for Swagger UI and Swagger Editor users:  \n"
            '>Cookie authentication iscurrently not supported for "try it out" requests due to browser '
            "securityrestrictions. See [this issue](https://github.com/swagger-api/swagger-js/issues/1163)"
            "for more information. [SwaggerHub](https://swagger.io/tools/swaggerhub/)does not have this limitation. "
        )
        assert route_dict["post"].parameters[0].in_ == "cookie"
        assert route_dict["post"].parameters[0].name == "cookie"
        assert route_dict["post"].parameters[0].required
        assert route_dict["post"].parameters[0].schema_ == {"type": "object"}

        assert route_dict["post"].parameters[1].description == "age"
        assert route_dict["post"].parameters[1].in_ == "path"
        assert route_dict["post"].parameters[1].name == "age"
        assert route_dict["post"].parameters[1].required
        assert route_dict["post"].parameters[1].schema_ == {
            "exclusiveMaximum": 100,
            "exclusiveMinimum": 1,
            "type": "integer",
        }

        assert route_dict["post"].parameters[2].description == "user name"
        assert route_dict["post"].parameters[2].in_ == "query"
        assert route_dict["post"].parameters[2].name == "multi_user_name"
        assert route_dict["post"].parameters[2].required
        assert route_dict["post"].parameters[2].schema_ == {
            "items": {"maxLength": 4, "minLength": 2, "type": "string"},
            "maxLength": 4,
            "minLength": 2,
            "type": "array",
        } or route_dict["post"].parameters[2].schema_ == {
            "items": {"type": "string"},
            "type": "array",
            "maxItems": 4,
            "minItems": 2,
        }

        assert route_dict["post"].parameters[3].description == "user id"
        assert route_dict["post"].parameters[3].in_ == "query"
        assert route_dict["post"].parameters[3].name == "uid"
        assert route_dict["post"].parameters[3].required
        assert route_dict["post"].parameters[3].schema_ == {
            "exclusiveMaximum": 1000,
            "exclusiveMinimum": 10,
            "type": "integer",
        }

        assert route_dict["post"].parameters[4].description == "user name"
        assert route_dict["post"].parameters[4].in_ == "query"
        assert route_dict["post"].parameters[4].name == "user_name"
        assert route_dict["post"].parameters[4].required
        assert route_dict["post"].parameters[4].schema_ == {"maxLength": 4, "minLength": 2, "type": "string"}

        assert route_dict["post"].parameters[5].description == "user email"
        assert route_dict["post"].parameters[5].in_ == "query"
        assert route_dict["post"].parameters[5].name == "email"
        assert route_dict["post"].parameters[5].schema_ == {"default": "example@xxx.com", "type": "string"}

        assert route_dict["post"].parameters[6].description == "sex"
        assert route_dict["post"].parameters[6].in_ == "query"
        assert route_dict["post"].parameters[6].name == "sex"
        assert route_dict["post"].parameters[6].required
        assert route_dict["post"].parameters[6].schema_ == {"allOf": [{"$ref": "#/components/schemas/SexEnum"}]}

        # If the type is typing.Any, then there will be no required
        assert route_dict["post"].request_body.content["multipart/form-data"].schema_ == {
            "properties": {"upload_file": {"format": "binary", "title": "Upload File", "type": "string"}},
            "required": ["upload_file"],
            "type": "object",
        } or route_dict["post"].request_body.content["multipart/form-data"].schema_ == {
            "properties": {"upload_file": {"format": "binary", "title": "Upload File", "type": "string"}},
            "type": "object",
        }

        rb_schema_key: str = (
            route_dict["post"].request_body.content["application/x-www-form-urlencoded"].schema_["$ref"]
        )
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]
        assert rb_schema["required"] == ["a", "b", "c"]
        assert rb_schema["properties"] == {
            "a": {"title": "A", "description": "form data", "type": "string"},
            "b": {"title": "B", "description": "form data", "type": "string"},
            "c": {
                "title": "C",
                "description": "form data     \n >Swagger UI could not support, when media_type is multipart/form-data",
                "type": "array",
                "items": {"type": "string"},
            },
        }

        self._test_simple_response_and_fail_response(route_dict["post"].responses)

    def test_pait_model_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/field/pait-model")

        assert any([i in route_dict["post"].operation_id for i in ["pait_model_route", "PaitModelHandler.post"]])
        assert route_dict["post"].tags == ["field"]

        assert route_dict["post"].pait_info["group"] == "field"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "test"  # type: ignore
        assert any(
            [i in route_dict["post"].pait_info["pait_id"] for i in ["pait_model_route", "PaitModelHandler.post"]]
        )

        assert route_dict["post"].parameters[0].description == "user agent"
        assert route_dict["post"].parameters[0].in_ == "header"
        assert route_dict["post"].parameters[0].name == "user-agent"
        assert route_dict["post"].parameters[0].required
        assert route_dict["post"].parameters[0].schema_ == {"type": "string"}

        assert route_dict["post"].parameters[1].description == "user id"
        assert route_dict["post"].parameters[1].in_ == "query"
        assert route_dict["post"].parameters[1].name == "uid"
        assert route_dict["post"].parameters[1].required
        assert route_dict["post"].parameters[1].schema_ == {
            "exclusiveMaximum": 1000,
            "exclusiveMinimum": 10,
            "type": "integer",
        }

        rb_schema_key: str = route_dict["post"].request_body.content["application/json"].schema_["$ref"]
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]
        rb_schema_key = rb_schema["properties"]["user_info"]["$ref"].split("/")[-1]
        rb_schema = self.pait_openapi.model.components["schemas"][rb_schema_key]
        assert rb_schema["required"] == ["user_name", "age"]
        assert rb_schema["properties"] == {
            "user_name": {
                "title": "User Name",
                "description": "user name",
                "maxLength": 4,
                "minLength": 2,
                "type": "string",
            },
            "age": {
                "title": "Age",
                "description": "age",
                "exclusiveMinimum": 1,
                "exclusiveMaximum": 100,
                "type": "integer",
            },
        }

        self._test_simple_response_and_fail_response(route_dict["post"].responses)


class _TestSecurityOpenAPI(BasicTestOpenAPI):
    def test_security_schemes(self) -> None:
        assert self.pait_openapi.model.components["securitySchemes"]["HTTPBasic"] == HttpSecurityModel(scheme="basic")
        assert self.pait_openapi.model.components["securitySchemes"]["HTTPBearer"] == HttpSecurityModel(scheme="bearer")
        assert self.pait_openapi.model.components["securitySchemes"]["HTTPDigest"] == HttpSecurityModel(scheme="digest")
        assert self.pait_openapi.model.components["securitySchemes"]["OAuth2PasswordBearer"] == Oauth2SecurityModel(
            flows=OAuthFlowsModel(
                password=OAuthFlowModel(
                    scopes={"user-info": "get all user info", "user-name": "only get user name"},
                    tokenUrl="/api/security/oauth2-login",
                ),
            )
        )
        assert self.pait_openapi.model.components["securitySchemes"]["token-cookie-api-key"] == ApiKeySecurityModel(
            in_stub="cookie", name="token"
        )
        assert self.pait_openapi.model.components["securitySchemes"]["token-header-api-key"] == ApiKeySecurityModel(
            in_stub="header", name="token"
        )
        assert self.pait_openapi.model.components["securitySchemes"]["token-query-api-key"] == ApiKeySecurityModel(
            in_stub="query", name="token"
        )

    def _test_http_security_route(self, security_type: str) -> None:
        security_dict = {"basic-credentials": "Basic"}
        route_dict = self.pait_openapi.model.paths.pop(f"/api/security/user-name-by-http-{security_type}")
        o_security_type = security_type.replace("-", "_")

        assert any(
            [
                i in route_dict["get"].operation_id
                for i in [
                    f"get_user_name_by_http_{o_security_type}",
                    "UserNameByHttpBasicCredentialsHandler.get",
                    "UserNameByHttpBearerHandler.get",
                    "UserNameByHttpDigestHandler.get",
                ]
            ]
        )
        assert route_dict["get"].security == [{f"HTTP{security_dict.get(security_type, security_type).title()}": []}]
        assert route_dict["get"].tags == ["depend", "security", "http"]

        assert route_dict["get"].pait_info["group"] == "security"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "test"  # type: ignore

        rp_schema_key = route_dict["get"].responses["200"].content["application/json"].schema_["$ref"]
        rp_schema_key = rp_schema_key.split("/")[-1]
        assert self.pait_openapi.model.components["schemas"][rp_schema_key] == _pydanitc_adapter.model_json_schema(
            response_model.SuccessRespModel.response_data
        )

        for status_code in ["401", "403"]:
            if status_code in route_dict["get"].responses:
                try:
                    assert route_dict["get"].responses[status_code].content["text/html"].schema_ == {
                        "example": "<h1> example html</h1>",
                        "type": "string",
                    }
                except KeyError:
                    assert route_dict["get"].responses[status_code].content["text/plain"].schema_ == {
                        "example": "example data",
                        "type": "string",
                    }
                break
        else:
            raise RuntimeError("Can not found error response model")

    def test_get_user_name_by_http_bearer_route(self) -> None:
        self._test_http_security_route("bearer")

    def test_get_user_name_by_http_digest_route(self) -> None:
        self._test_http_security_route("digest")

    def test_get_user_name_by_http_basic_credentials_route(self) -> None:
        self._test_http_security_route("basic-credentials")

    def _test_http_api_key_route(self, security_type: str) -> None:
        route_dict = self.pait_openapi.model.paths.pop(f"/api/security/api-{security_type}-key")
        assert (
            f"api_key_{security_type}_route" in route_dict["get"].operation_id
            or f"APIKey{security_type.title()}Handler" in route_dict["get"].operation_id
        )
        assert route_dict["get"].security == [{f"token-{security_type}-api-key": []}]
        assert route_dict["get"].tags == ["depend", "security", "api-key"]

        assert route_dict["get"].pait_info["group"] == "security"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "test"  # type: ignore
        assert (
            f"api_key_{security_type}_route" in route_dict["get"].pait_info["pait_id"]
            or f"APIKey{security_type.title()}Handler" in route_dict["get"].pait_info["pait_id"]
        )  # type: ignore

        rp_schema_key = route_dict["get"].responses["200"].content["application/json"].schema_["$ref"]
        rp_schema_key = rp_schema_key.split("/")[-1]
        assert self.pait_openapi.model.components["schemas"][rp_schema_key] == _pydanitc_adapter.model_json_schema(
            response_model.SuccessRespModel.response_data
        )
        try:
            assert route_dict["get"].responses["403"].content["text/html"].schema_ == {
                "example": "<h1> example html</h1>",
                "type": "string",
            }
        except KeyError:
            # support starlette
            assert route_dict["get"].responses["403"].content["text/plain"].schema_ == {
                "example": "example data",
                "type": "string",
            }

    def test_api_key_cookie_route(self) -> None:
        self._test_http_api_key_route("cookie")

    def test_api_key_header_route(self) -> None:
        self._test_http_api_key_route("header")

    def test_api_key_query_route(self) -> None:
        self._test_http_api_key_route("query")

    def _test_oauth2_route(self, security_type: str) -> None:
        route_dict = self.pait_openapi.model.paths.pop(f"/api/security/oauth2-user-{security_type}")

        assert any(
            [
                i in route_dict["get"].operation_id
                for i in [f"oauth2_user_{security_type}", f"OAuth2User{security_type.title()}Handler.get"]
            ]
        )
        assert route_dict["get"].security == [{"OAuth2PasswordBearer": [f"user-{security_type}"]}]
        assert route_dict["get"].tags == ["depend", "security", "oauth2"]

        assert route_dict["get"].pait_info["group"] == "security"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "test"  # type: ignore
        assert any(
            [
                i in route_dict["get"].pait_info["pait_id"]
                for i in [f"oauth2_user_{security_type}", f"OAuth2User{security_type.title()}Handler.get"]
            ]
        )

        rp_schema_key = route_dict["get"].responses["200"].content["application/json"].schema_["$ref"]
        rp_schema_key = rp_schema_key.split("/")[-1]
        assert self.pait_openapi.model.components["schemas"][rp_schema_key] == _pydanitc_adapter.model_json_schema(
            response_model.SuccessRespModel.response_data
        )
        for status_code in ["400", "401"]:
            try:
                assert route_dict["get"].responses[status_code].content["text/html"].schema_ == {
                    "example": "<h1> example html</h1>",
                    "type": "string",
                }
            except KeyError:
                assert route_dict["get"].responses[status_code].content["text/plain"].schema_ == {
                    "example": "example data",
                    "type": "string",
                }

    def test_oauth2_user_name(self) -> None:
        self._test_oauth2_route("name")

    def test_oauth2_user_info(self) -> None:
        self._test_oauth2_route("info")

    def test_oauth2_login(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/security/oauth2-login")

        assert any([i in route_dict["post"].operation_id for i in ["oauth2_login", "OAuth2LoginHandler.post"]])
        assert route_dict["post"].security is None
        assert route_dict["post"].tags == ["depend", "security", "oauth2"]

        assert route_dict["post"].pait_info["group"] == "security"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "test"  # type: ignore

        assert any([i in route_dict["post"].pait_info["pait_id"] for i in ["oauth2_login", "OAuth2LoginHandler.post"]])

        rb_schema_key: str = (
            route_dict["post"].request_body.content["application/x-www-form-urlencoded"].schema_["$ref"]
        )
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]
        rb_schema.pop("title")
        self._test_nested_model(
            rb_schema,
            _pydanitc_adapter.model_json_schema(OAuth2PasswordRequestFrom),
            _pydanitc_adapter.model_json_schema(OAuth2PasswordRequestFrom),
        )


class _TestResponseOpenAPI(BasicTestOpenAPI):
    def test_check_response_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/resp/check-resp")

        assert route_dict["get"].description == "Test test-helper check response"
        assert (
            "check_response_route" in route_dict["get"].operation_id
            or "CheckRespHandler.get" in route_dict["get"].operation_id
        )
        assert route_dict["get"].tags == ["check resp", "user"]

        assert route_dict["get"].pait_info["group"] == "check_resp"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "release"  # type: ignore
        assert (
            "check_response_route" in route_dict["get"].pait_info["pait_id"]
            or "CheckRespHandler.get" in route_dict["get"].pait_info["pait_id"]
        )  # type: ignore

        assert route_dict["get"].parameters[0].description == "user id"
        assert route_dict["get"].parameters[0].in_ == "query"
        assert route_dict["get"].parameters[0].name == "uid"
        assert route_dict["get"].parameters[0].required
        assert route_dict["get"].parameters[0].schema_ == {
            "exclusiveMaximum": 1000,
            "exclusiveMinimum": 10,
            "type": "integer",
        }

        assert route_dict["get"].parameters[1].description == "user email"
        assert route_dict["get"].parameters[1].in_ == "query"
        assert route_dict["get"].parameters[1].name == "email"
        assert route_dict["get"].parameters[1].schema_ == {"default": "example@xxx.com", "type": "string"}

        assert route_dict["get"].parameters[2].description == "user name"
        assert route_dict["get"].parameters[2].in_ == "query"
        assert route_dict["get"].parameters[2].name == "user_name"
        assert route_dict["get"].parameters[2].required
        assert route_dict["get"].parameters[2].schema_ == {"maxLength": 4, "minLength": 2, "type": "string"}

        assert route_dict["get"].parameters[3].description == "age"
        assert route_dict["get"].parameters[3].in_ == "query"
        assert route_dict["get"].parameters[3].name == "age"
        assert route_dict["get"].parameters[3].required
        assert route_dict["get"].parameters[3].schema_ == {
            "exclusiveMaximum": 100,
            "exclusiveMinimum": 1,
            "type": "integer",
        }

        assert route_dict["get"].parameters[4].description == "display age"
        assert route_dict["get"].parameters[4].in_ == "query"
        assert route_dict["get"].parameters[4].name == "display_age"
        assert route_dict["get"].parameters[4].schema_ == {"default": 0, "type": "integer"}

        self._test_success_response_and_fail_response(route_dict["get"].responses, response_model.UserSuccessRespModel3)

    def _test_response(self, resp_type: str, resp_model: Type[BaseResponseModel]) -> None:
        for path in [f"/api/resp/{resp_type}-resp", f"/api/resp/async-{resp_type}-resp"]:
            if path not in self.pait_openapi.model.paths:
                continue
            route_dict = self.pait_openapi.model.paths.pop(path)

            assert any(
                [
                    i in route_dict["get"].operation_id
                    for i in [f"{resp_type}_response_route", f"{resp_type.title()}ResponseHanler.get"]
                ]
            )
            assert route_dict["get"].description == f"test return {resp_type} response"
            assert route_dict["get"].tags == ["check resp"]

            assert route_dict["get"].pait_info["group"] == "check_resp"  # type: ignore
            assert route_dict["get"].pait_info["status"] == "release"  # type: ignore
            assert any(
                [
                    i in route_dict["get"].pait_info["pait_id"]
                    for i in [f"{resp_type}_response_route", f"{resp_type.title()}ResponseHanler.get"]
                ]
            )

            assert route_dict["get"].responses["200"].description == resp_model.description
            assert (
                route_dict["get"].responses["200"].content[resp_model.media_type].schema_ == resp_model.openapi_schema
            )

    def test_text_response_route(self) -> None:
        self._test_response("text", response_model.TextRespModel)

    def test_html_response_route(self) -> None:
        self._test_response("html", response_model.HtmlRespModel)

    def test_file_response_route(self) -> None:
        self._test_response("file", response_model.FileRespModel)


class _TestOtherOpenAPI(BasicTestOpenAPI):
    def test_raise_tip_route(self) -> None:
        for path in ["/api/raise-tip", "/api/raise-not-tip"]:
            route_dict = self.pait_openapi.model.paths.pop(path)
            route_name = path.split("/")[-1].replace("-", "_")
            assert any(
                [
                    i in route_dict["post"].operation_id
                    for i in [f"{route_name}_route", "RaiseTipHandler.post", "RaiseNotTipHandler.post"]
                ]
            )
            assert route_dict["post"].deprecated
            assert route_dict["post"].description == "test pait raise tip"
            assert route_dict["post"].tags == ["raise"]

            assert route_dict["post"].pait_info["group"] == "other"  # type: ignore
            assert route_dict["post"].pait_info["status"] == "abandoned"  # type: ignore

            assert any(
                [
                    i in route_dict["post"].pait_info["pait_id"]
                    for i in [f"{route_name}_route", "RaiseTipHandler.post", "RaiseNotTipHandler.post"]
                ]
            )

            assert route_dict["post"].parameters[0].description == "Content-Type"
            assert route_dict["post"].parameters[0].in_ == "header"
            assert route_dict["post"].parameters[0].name == "content__type"
            assert route_dict["post"].parameters[0].required
            assert route_dict["post"].parameters[0].schema_ == {"type": "string"}

            self._test_simple_response_and_fail_response(route_dict["post"].responses)

    def test_cbv_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/cbv")

        assert route_dict["get"].description == "Text cbv route get"
        assert any([i in route_dict["get"].operation_id for i in ["test_cbv.get", "CbvRoute", "CbvHandler.get"]])
        assert route_dict["get"].tags == ["cbv"]

        assert route_dict["get"].pait_info["group"] == "user"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "release"  # type: ignore
        assert any([i in route_dict["get"].pait_info["pait_id"] for i in ["CbvRoute.get", "CbvHandler.get"]])

        assert route_dict["get"].parameters[0].in_ == "header"
        assert route_dict["get"].parameters[0].name == "Content-Type"
        assert route_dict["get"].parameters[0].required
        assert route_dict["get"].parameters[0].schema_ == {"type": "string"}

        assert route_dict["get"].parameters[1].description == "age"
        assert route_dict["get"].parameters[1].in_ == "query"
        assert route_dict["get"].parameters[1].name == "age"
        assert route_dict["get"].parameters[1].required
        assert route_dict["get"].parameters[1].schema_ == {
            "exclusiveMaximum": 100,
            "exclusiveMinimum": 1,
            "type": "integer",
        }

        assert route_dict["get"].parameters[2].description == "user id"
        assert route_dict["get"].parameters[2].in_ == "query"
        assert route_dict["get"].parameters[2].name == "uid"
        assert route_dict["get"].parameters[2].required
        assert route_dict["get"].parameters[2].schema_ == {
            "exclusiveMaximum": 1000,
            "exclusiveMinimum": 10,
            "type": "integer",
        }

        assert route_dict["get"].parameters[3].description == "user name"
        assert route_dict["get"].parameters[3].in_ == "query"
        assert route_dict["get"].parameters[3].name == "user_name"
        assert route_dict["get"].parameters[3].required
        assert route_dict["get"].parameters[3].schema_ == {"maxLength": 4, "minLength": 2, "type": "string"}

        assert route_dict["get"].parameters[4].description == "sex"
        assert route_dict["get"].parameters[4].in_ == "query"
        assert route_dict["get"].parameters[4].name == "sex"
        assert route_dict["get"].parameters[4].required
        assert route_dict["get"].parameters[4].schema_ == {"allOf": [{"$ref": "#/components/schemas/SexEnum"}]}

        self._test_success_response_and_fail_response(
            route_dict["get"].responses, create_json_response_model(response_model.UserSuccessRespModel)
        )

        assert route_dict["post"].description == "test cbv post method"
        assert any([i in route_dict["post"].operation_id for i in ["test_cbv.post", "CbvRoute", "CbvHandler.post"]])
        assert route_dict["post"].tags == ["cbv"]

        assert route_dict["post"].pait_info["group"] == "user"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "release"  # type: ignore

        assert any([i in route_dict["post"].pait_info["pait_id"] for i in ["CbvRoute.post", "CbvHandler.post"]])

        assert route_dict["post"].parameters[0].in_ == "header"
        assert route_dict["post"].parameters[0].name == "Content-Type"
        assert route_dict["post"].parameters[0].required
        assert route_dict["post"].parameters[0].schema_ == {"type": "string"}

        rb_schema_key: str = route_dict["post"].request_body.content["application/json"].schema_["$ref"]
        rb_schema_key = rb_schema_key.split("/")[-1]
        rb_schema: dict = self.pait_openapi.model.components["schemas"][rb_schema_key]

        assert rb_schema["required"] == ["age", "uid", "user_name", "sex"]
        assert rb_schema["properties"] == {
            "age": {
                "title": "Age",
                "description": "age",
                "exclusiveMinimum": 1,
                "exclusiveMaximum": 100,
                "example": 25,
                "type": "integer",
            },
            "uid": {
                "title": "Uid",
                "description": "user id",
                "exclusiveMinimum": 10,
                "exclusiveMaximum": 1000,
                "type": "integer",
            },
            "user_name": {
                "title": "User Name",
                "description": "user name",
                "maxLength": 4,
                "minLength": 2,
                "type": "string",
            },
            "sex": {"description": "sex", "allOf": [{"$ref": "#/components/schemas/SexEnum"}]},
        }
        self._test_success_response_and_fail_response(
            route_dict["post"].responses, create_json_response_model(response_model.UserSuccessRespModel)
        )

    def test_not_pait_cbv_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/not-pait-cbv")

        for http_method in ["get", "post"]:  # type: HttpMethodLiteral
            assert any(
                [
                    i in route_dict[http_method].operation_id
                    for i in [f"NotPaitRoute.{http_method}", "NotPaitCbvRoute", f"NotPaitCbvHandler.{http_method}"]
                ]
            )
            assert route_dict[http_method].tags == ["default"]

            assert route_dict[http_method].pait_info["group"] == "root"  # type: ignore
            assert route_dict[http_method].pait_info["status"] == "undefined"  # type: ignore

            assert any(
                [
                    i in route_dict[http_method].pait_info["pait_id"]
                    for i in [f"NotPaitRoute.{http_method}", "NotPaitCbvRoute", f"NotPaitCbvHandler.{http_method}"]
                ]
            )

            assert route_dict[http_method].parameters[0].in_ == "query"
            assert route_dict[http_method].parameters[0].name == "user_name"
            assert route_dict[http_method].parameters[0].required
            assert route_dict[http_method].parameters[0].schema_ == {"type": "string"}

    def test_login_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/login")

        assert any([i in route_dict["post"].operation_id for i in ["login_route", "LoginHandler.post"]])
        assert route_dict["post"].tags == ["links"]

        assert route_dict["post"].pait_info["group"] == "links"  # type: ignore
        assert route_dict["post"].pait_info["status"] == "release"  # type: ignore
        assert any([i in route_dict["post"].pait_info["pait_id"] for i in ["login_route", "LoginHandler.post"]])

        assert route_dict["post"].responses["200"].description == response_model.LoginRespModel.description
        rp_schema_key = route_dict["post"].responses["200"].content["application/json"].schema_["$ref"]
        rp_schema_key = rp_schema_key.split("/")[-1]

        self._test_nested_model(
            self.pait_openapi.model.components["schemas"][rp_schema_key],
            _pydanitc_adapter.model_json_schema(response_model.LoginRespModel.response_data),
            _pydanitc_adapter.model_json_schema(response_model.LoginRespModel.response_data),
        )

        for key in [
            "example.flask_example.main_example_get_user_route/header/token",
            "example.sanic_example.main_example_get_user_route/header/token",
            "example.starlette_example.main_example_get_user_route/header/token",
            "example.tornado_example.main_example_GetUserHandler.get/header/token",
        ]:
            if key not in route_dict["post"].responses["200"].links:
                continue
            assert (
                route_dict["post"].responses["200"].links[key].description == response_model.link_login_token_model.desc
            )
            assert (
                route_dict["post"].responses["200"].links[key].parameters["token"]
                == response_model.link_login_token_model.openapi_runtime_expr
            )
            break
        else:
            raise AssertionError("link not found")

    def test_get_user_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/user")

        assert any([i in route_dict["get"].operation_id for i in ["get_user_route", "GetUserHandler.get"]])
        assert route_dict["get"].tags == ["links"]

        assert route_dict["get"].pait_info["group"] == "links"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "release"  # type: ignore
        assert any([i in route_dict["get"].pait_info["pait_id"] for i in ["get_user_route", "GetUserHandler.get"]])

        assert route_dict["get"].parameters[0].description == "token"
        assert route_dict["get"].parameters[0].in_ == "header"
        assert route_dict["get"].parameters[0].name == "token"
        assert route_dict["get"].parameters[0].schema_["default"] == ""
        assert route_dict["get"].parameters[0].schema_["type"] == "string"

        rp_schema_key = route_dict["get"].responses["200"].content["application/json"].schema_["$ref"]
        rp_schema_key = rp_schema_key.split("/")[-1]

        self._test_nested_model(
            self.pait_openapi.model.components["schemas"][rp_schema_key],
            _pydanitc_adapter.model_json_schema(response_model.SuccessRespModel.response_data),
            _pydanitc_adapter.model_json_schema(response_model.SuccessRespModel.response_data),
        )

    def test_not_pait_route(self) -> None:
        if self.app.__class__.__name__ == "Application":
            return
        route_dict = self.pait_openapi.model.paths.pop("/api/not-pait")

        assert any([i in route_dict["get"].operation_id for i in ["not_pait_route", "NotPaitCbvHandler.get"]])
        assert route_dict["get"].tags == ["default"]

        assert route_dict["get"].pait_info["group"] == "root"  # type: ignore
        assert route_dict["get"].pait_info["status"] == "undefined"  # type: ignore
        assert any([i in route_dict["get"].pait_info["pait_id"] for i in ["not_pait_route", "NotPaitCbvHandler.get"]])

        assert route_dict["get"].parameters[0].in_ == "query"
        assert route_dict["get"].parameters[0].name == "user_name"
        assert route_dict["get"].parameters[0].required
        assert route_dict["get"].parameters[0].schema_ == {"type": "string"}

    def test_tag_route(self) -> None:
        route_dict = self.pait_openapi.model.paths.pop("/api/tag")
        assert len(route_dict["get"].tags) == 1
        assert route_dict["get"].tags[0] == "include"

    def test_api_route(self) -> None:
        user_info_dict = self.pait_openapi.model.paths.pop("/api/user/info")
        user_info_dict["get"].tags = ["user", "root api"]

        login_dict = self.pait_openapi.model.paths.pop("/api/user/login")
        login_dict["post"].tags = ["user", "root api"]

        health_dict = self.pait_openapi.model.paths.pop("/api/health")
        health_dict["get"].tags = ["root api"]


class BaseTestOpenAPI(
    _TestDependOpenAPI, _TestFieldOpenAPI, _TestSecurityOpenAPI, _TestResponseOpenAPI, _TestOtherOpenAPI
):
    def test_all(self, exclude_test_name_list: Optional[List[str]] = None) -> None:
        exclude_test_name_list = exclude_test_name_list or []
        exclude_test_name_list.append("test_all")
        for i in dir(self):
            if i in exclude_test_name_list:
                continue
            if i.startswith("test_"):
                try:
                    getattr(self, i)()
                except AssertionError as e:
                    print(i)
                    raise e

        ignore_test_path_set = {
            "/api/field/any-type",
            "/api/user/cbv",
            "/api/depend/pre-depend",
            "/api/new-raise-not-tip",
        }
        for path in list(self.pait_openapi.model.paths.keys()):
            if path.startswith("/api/plugin") or path.startswith("/api/sync-to-thread"):
                # Plugin related routes are ignored because there is nothing new in the Open API they generate
                self.pait_openapi.model.paths.pop(path)
            if path in ignore_test_path_set:
                # Ignore routes that don't need to be tested
                self.pait_openapi.model.paths.pop(path)
        # Confirm that all APIs have been tested
        assert not self.pait_openapi.model.paths
