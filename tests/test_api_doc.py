from example.api_doc import flask_example, starlette_example, sanic_example, tornado_example


class TestApiDoc:
    def test_flask(self) -> None:
        """Now, ignore test api doc"""
        app_name: str = flask_example.load_app(flask_example.create_app())
        flask_example.PaitMd(app_name, use_html_details=True)
        flask_example.PaitJson(app_name, indent=2)
        flask_example.PaitYaml(app_name, )
        for i in ("json", "yaml"):
            flask_example.PaitOpenApi(app_name, title="Pait Doc", type_=i)

    def test_starlette(self) -> None:
        """Now, ignore test api doc"""
        app_name: str = starlette_example.load_app(starlette_example.create_app())
        starlette_example.PaitMd(app_name, use_html_details=True)
        starlette_example.PaitJson(app_name, indent=2)
        starlette_example.PaitYaml(app_name)
        for i in ("json", "yaml"):
            starlette_example.PaitOpenApi(
                app_name,
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

    def test_sanic(self) -> None:
        """Now, ignore test api doc"""
        app_name: str = sanic_example.load_app(sanic_example.create_app())
        sanic_example.PaitMd(app_name, use_html_details=True)
        sanic_example.PaitJson(app_name, indent=2)
        sanic_example.PaitYaml(app_name)
        for i in ("json", "yaml"):
            sanic_example.PaitOpenApi(
                app_name,
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

    def test_tornado(self) -> None:
        """Now, ignore test api doc"""
        app_name: str = tornado_example.load_app(tornado_example.create_app())
        tornado_example.PaitMd(app_name, use_html_details=True)
        tornado_example.PaitJson(app_name, indent=2)
        tornado_example.PaitYaml(app_name)
        for i in ("json", "yaml"):
            tornado_example.PaitOpenApi(
                app_name,
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"},
                    {"name": "user", "description": "user api"},
                ],
                type_=i,
            )

