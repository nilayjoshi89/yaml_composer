import os
from pathlib import Path
from typing import Any

import yaml

from py_yaml_composer.utility.app_config import AppConfig
from py_yaml_composer.utility.files.base import YamlFileHelperBase


class YamlFileHelper(YamlFileHelperBase):
    def load(self, file_path: str) -> dict[Any, Any]:
        file_path = self.get_workspace_path(file_path)
        with open(file_path) as f:
            return dict(yaml.safe_load(f))

    def save(self, data: dict[Any, Any], file_path: str) -> None:
        file_path = self.get_workspace_path(file_path)
        with open(file_path, "w") as f:
            yaml.safe_dump(
                data, f, default_flow_style=False, sort_keys=False, width=9999
            )

    def exists(self, file_path: str) -> bool:
        file_path = self.get_workspace_path(file_path)
        return os.path.exists(file_path)

    def get_workspace_path(self, file_path: str) -> str:
        if Path(file_path).is_absolute():
            return file_path

        return str(Path(AppConfig.Workspace).joinpath(file_path))
