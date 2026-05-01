from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext


class YamlComplexActions(YamlActionBase):
    def __init__(self, actions: list[YamlActionBase]) -> None:
        self.actions = actions

    def apply(
        self, data: dict[Any, Any] | list[Any] | Any, context: ActionContext
    ) -> None:
        for action in self.actions:
            action.apply(data, context)
