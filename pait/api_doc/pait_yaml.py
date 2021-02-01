from typing import Any, Dict, Optional

import yaml

from .base_parse import PaitBaseParse


class PaitYaml(PaitBaseParse):
    def __init__(self, title: str = "Pait Yaml", filename: Optional[str] = None):
        super().__init__(undefined="Required")

        pait_dict: Dict[str, Any] = self.gen_dict()
        pait_dict["title"] = title

        pait_yaml: str = yaml.dump(pait_dict)
        self.output(filename, pait_yaml, ".yaml")
