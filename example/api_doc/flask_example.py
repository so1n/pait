from example.param_verify.flask_example import app
from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app

filename: str = "./example_doc/flask_pait"
load_app(app)
PaitMd(use_html_details=True, filename=filename)
PaitJson(filename=filename, indent=2)
PaitYaml(filename=filename)
for i in ("json", "yaml"):
    PaitOpenApi(title="Pait Doc", filename=filename + "_openapi", type_=i)
