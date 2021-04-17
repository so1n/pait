import argparse
import importlib
from typing import Dict, List, Optional

from pait.api_doc.markdown import PaitMd
from pait.api_doc.open_api import PaitOpenApi
from pait.api_doc.pait_json import PaitJson
from pait.api_doc.pait_yaml import PaitYaml
from pait.app import load_app
from pait.model import PaitCoreModel

if __name__ == "__main__":
    output_type_list: List[str] = ["md", "json", "yaml", "openapi_json", "openapi_yaml"]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "app",
        help="Enter the file name and app name of the app that needs to generate the document,"
        " for example:app stands for. /example.py app",
    )
    parser.add_argument("-o", "--output_type", help=f"now support: {','.join(output_type_list)}")
    parser.add_argument("-t", "--title", help="Title of doc", default="Pait Doc")
    parser.add_argument("-f", "--filename", help="Name of save file", default=None)
    parser.add_argument(
        "-u", "--use_html_details", help="Whether to output html text in the md document", default=True, type=bool
    )
    parser.add_argument("-i", "--indent", help="json formatted output of indent values", default=2, type=int)

    args, unknown = parser.parse_known_args()

    module_name, app_name = args.app.split(":")
    input_output_type_list: List[str] = [i for i in args.output_type.split(",") if i in output_type_list]
    title: str = args.title
    filename: Optional[str] = args.filename
    use_html_details: bool = args.use_html_details
    indent: int = args.indent

    module = importlib.import_module(module_name)
    app = getattr(module, app_name, None)
    if not app:
        raise ImportError(f"Can't found {app} in {module}")
    pait_dict: Dict[str, PaitCoreModel] = load_app(app)

    for type_ in input_output_type_list:
        if type_ == "md":
            PaitMd(pait_dict, title=title, filename=filename, use_html_details=use_html_details)
        elif type_ == "json":
            PaitJson(pait_dict, title=title, filename=filename, indent=indent)
        elif type_ == "yaml":
            PaitYaml(pait_dict, title=title, filename=filename)
        elif type_ == "openapi_json":
            PaitOpenApi(pait_dict, title=title, filename=filename, type_="json")
        elif type_ == "openapi_yaml":
            PaitOpenApi(pait_dict, title=title, filename=filename, type_="yaml")
        else:
            raise ValueError(f"Not support output type: {type_}, please select from the following options")
