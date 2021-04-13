from example.param_verify.tornado_example import create_app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app

if __name__ == "__main__":
    filename: str = "./example_doc/tornado"
    app_name: str = load_app(create_app())
    PaitMd(app_name, use_html_details=True, filename=filename)
    PaitJson(app_name, filename=filename, indent=2)
    PaitYaml(app_name, filename=filename)

    for i in ("json", "yaml"):
        PaitOpenApi(
            app_name,
            title="Pait Doc",
            open_api_tag_list=[
                {"name": "test", "description": "test api"},
                {"name": "user", "description": "user api"},
            ],
            type_=i,
            filename=filename + "_openapi",
        )
