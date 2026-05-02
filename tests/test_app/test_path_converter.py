from pait.app.flask._load_app import get_openapi_path as get_flask_openapi_path
from pait.app.flask._simple_route import default_replace_openapi_url_to_url as replace_flask_url
from pait.app.sanic._load_app import get_openapi_path as get_sanic_openapi_path
from pait.app.sanic._simple_route import default_replace_openapi_url_to_url as replace_sanic_url
from pait.app.tornado._load_app import get_openapi_path as get_tornado_openapi_path
from pait.app.tornado._simple_route import default_replace_openapi_url_to_url as replace_tornado_url


def test_flask_path_converter() -> None:
    assert "/user/{user_id}/file/{file_path}" == get_flask_openapi_path("user/<int:user_id>/file/<path:file_path>")
    assert "http://google.com/user/<path:user_id>/post" == replace_flask_url("http://google.com/user/{user_id}/post")
    assert "/user/<path:user_id>/post" == replace_flask_url("/user/{user_id:int}/post")


def test_sanic_path_converter() -> None:
    assert "/user/{user_id}/file/{file_path}" == get_sanic_openapi_path("user/<user_id:int>/file/<file_path:path>")
    assert "http://google.com/user/<user_id>/post" == replace_sanic_url("http://google.com/user/{user_id}/post")
    assert "/user/<user_id>/post" == replace_sanic_url("/user/{user_id:int}/post")


def test_tornado_path_converter() -> None:
    assert r"/user/{user_id}/file/{file_path}" == get_tornado_openapi_path(
        r"user/(?P<user_id>\w+)/file/(?P<file_path>.+)"
    )
    assert "/user/{user_id}/post" == get_tornado_openapi_path("/user/<user_id>/post")
    assert r"http://google.com/user/(?P<user_id>\w+)/post" == replace_tornado_url(
        "http://google.com/user/{user_id}/post"
    )
    assert r"/user/(?P<user_id>\w+)/post" == replace_tornado_url("/user/{user_id:int}/post")
