from example.api_doc import flask_example, starlette_example


class TestApiDoc:
    def atest(self) -> None:
        """Now, ignore test api doc"""
        flask_example.load_app(flask_example.app)
        flask_example.PaitMd(use_html_details=True)
        flask_example.PaitJson(indent=2)
        flask_example.PaitYaml()
        for i in ("json", "yaml"):
            flask_example.PaitOpenApi(title="Pait Doc", type_=i)

        starlette_example.load_app(starlette_example.app)
        starlette_example.PaitMd(use_html_details=True)
        starlette_example.PaitJson(indent=2)
        starlette_example.PaitYaml()
        for i in ("json", "yaml"):
            starlette_example.PaitOpenApi(
                title="Pait Doc",
                open_api_tag_list=[
                    {"name": "test", "description": "test api"}, {"name": "user", "description": "user api"}
                ],
                type_=i
            )
