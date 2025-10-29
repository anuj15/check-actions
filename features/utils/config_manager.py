import os
from pathlib import Path

import yaml


def is_ci():
    return os.getenv("GITHUB_ACTIONS", "false").lower() == "true"


class ConfigManager:

    def __init__(self):
        self.root_dir = os.getenv("GITHUB_WORKSPACE") or str(Path(__file__).resolve().parents[2])
        config_path = Path(self.root_dir) / "config.yml"
        with open(config_path, encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get(self, pstr_key):
        str_env = os.getenv('ENVIRONMENT') or self.data['environment']
        str_env_config = self.data[str_env]
        value = os.getenv(pstr_key)
        if value is not None:
            return value
        return str_env_config.get(pstr_key, self.data.get(pstr_key))
