from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.complex_action import YamlComplexActions
from py_yaml_composer.actions.sort_action import YamlSortDockerComposeNodeAction
from py_yaml_composer.actions.xref_action import YamlXRefAction


class DefaultActions:
    @staticmethod
    def get() -> list[YamlActionBase]:
        return [
            YamlComplexActions(
                [YamlXRefAction(), YamlSortDockerComposeNodeAction()]
            )
        ]
