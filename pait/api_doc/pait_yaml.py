from typing import Any, Dict, Optional

import yaml

from pait.model import PaitCoreModel

from .base_parse import PaitBaseParse  # type: ignore


class PaitYaml(PaitBaseParse):
    def __init__(self, pait_dict: Dict[str, PaitCoreModel], title: str = "Pait Yaml", filename: Optional[str] = None):
        super().__init__(pait_dict, undefined="Required")

        _pait_dict: Dict[str, Any] = self.gen_dict()
        _pait_dict["title"] = title

        pait_yaml: str = yaml.dump(_pait_dict)
        self.output(filename, pait_yaml, ".yaml")
