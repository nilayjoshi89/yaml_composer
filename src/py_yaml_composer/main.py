import sys

from py_yaml_composer.actions.default_actions import DefaultActions
from py_yaml_composer.generator.yaml_generator import YamlGenerator
from py_yaml_composer.traverser.basic_dfs import YamlTraverser
from py_yaml_composer.utility.app_config import AppConfig
from py_yaml_composer.utility.files.yaml_helper import YamlFileHelper


def entry_point() -> None:
    AppConfig.parse_arg()
    print(
        YamlGenerator(
            file_helper=YamlFileHelper(),
            traverser=YamlTraverser(),
            multistage_actions=DefaultActions.get(),
        ).start(file_path=AppConfig.Filename)
    )

    sys.exit(0)
