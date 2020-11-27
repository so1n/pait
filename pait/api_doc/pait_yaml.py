import yaml
from typing import Any, Dict, Optional

from .base_parse import PaitBaseParse


class PaitYaml(PaitBaseParse):
    def __init__(self, title: str = 'Pait Yaml', filename: Optional[str] = None):
        super().__init__()

        pait_dict: Dict[str, Any] = self.gen_dict()
        pait_dict['title'] = title

        pait_yaml: str = yaml.dump(pait_dict)
        self.output_file(filename, pait_yaml, '.yaml')
