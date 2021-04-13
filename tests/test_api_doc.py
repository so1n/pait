from example.api_doc import flask_example, starlette_example, sanic_example, tornado_example


class TestApiDoc:
    def test_flask(self) -> None:
        """Now, ignore test api doc"""
        flask_example.load_app(flask_example.create_app())
        flask_example.PaitMd(use_html_details=True)
        flask_example.PaitJson(indent=2)
        flask_example.PaitYaml()
        for i in ("json", "yaml"):
            flask_example.PaitOpenApi(title="Pait Doc", type_=i)

    def test_starlette(self) -> None:
        """Now, ignore test api doc"""
        starlette_example.load_app(starlette_example.create_app())
        starlette_example.PaitMd(use_html_details=True)
        starlette_example.PaitJson(indent=2)
        starlette_example.PaitYaml()
        for i in ("json", "yaml"):
            starlette_example.PaitOpenApi(
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

    def test_sanic(self) -> None:
        """Now, ignore test api doc"""
        sanic_example.load_app(sanic_example.create_app())
        sanic_example.PaitMd(use_html_details=True)
        sanic_example.PaitJson(indent=2)
        sanic_example.PaitYaml()
        for i in ("json", "yaml"):
            sanic_example.PaitOpenApi(
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

    def test_tornado(self) -> None:
        """Now, ignore test api doc"""
        tornado_example.load_app(tornado_example.create_app())
        tornado_example.PaitMd(use_html_details=True)
        tornado_example.PaitJson(indent=2)
        tornado_example.PaitYaml()
        for i in ("json", "yaml"):
            tornado_example.PaitOpenApi(
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

