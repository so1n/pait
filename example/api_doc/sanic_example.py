from example.param_verify.sanic_example import app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app


if __name__ == "__main__":
    filename: str = "./example_doc/sanic"
    load_app(app)
    PaitMd(use_html_details=True, filename=filename)
    PaitJson(filename=filename, indent=2)
    PaitYaml(filename=filename)

    for i in ("json", "yaml"):
        PaitOpenApi(
            title="Pait Doc",
            open_api_tag_list=[
                {"name": "test", "description": "test api"}, {"name": "user", "description": "user api"}
            ],
            type_=i,
            filename=filename + "_openapi",
        )
