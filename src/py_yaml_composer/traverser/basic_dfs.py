from typing import Any

from py_yaml_composer.actions.action_base import YamlActionBase
from py_yaml_composer.actions.action_context import ActionContext
from py_yaml_composer.traverser.base import YamlTraverseBase


class YamlTraverser(YamlTraverseBase):
    def traverse(
        self,
        data: dict[Any, Any],
        handler: YamlActionBase,
        context: ActionContext,
    ) -> None:
        self.handler = handler
        self.context = context
        self.__traverse_internal(data)

    def __traverse_internal(self, current_node: Any) -> None:

        self.handler.apply(current_node, self.context)

        # dict
        if isinstance(current_node, dict):
            for val in current_node.values():
                self.__traverse_internal(val)
            return

        # list
        if isinstance(current_node, list):
            for item in current_node:
                self.__traverse_internal(item)
            return
